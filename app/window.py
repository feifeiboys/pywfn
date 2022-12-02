import sys
import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"
import pyvista as pv

from PySide6.QtWidgets import QFileDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel
from PySide6.QtGui import QIcon,QFont
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor, MainWindow


from pywfn.base import Mol
from pywfn.bondorder import piDM,piSH
from pywfn.readers import get_reader

from .plotter.canvas import Canvas
from .commands import Command
from .ui_app import Ui_MainWindow
from .setting import settingManager
from .update import Updater

from typing import *
from pathlib import Path

from .pages.setting import SettingWidget
from .pages.start import StartWidget
from .pages.orbital import OrbitalWidget

class Window(MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setting=settingManager()
        self.ui:Ui_MainWindow=Ui_MainWindow()
        self.ui.setupUi(self)
        

        self.commandLine=Command(self)
        self.ui.log.setFont(QFont('Courier New'))
        # self.ui.lineEdit.returnPressed.connect(self.command)
        
        self.init_menu()

        # self.ui.listWidget_files.itemClicked.connect(self.selectFile)
        # self.ui.listWidget_orbitals.itemClicked.connect(self.selectOrbital) # 点击分子轨道名时触发的事件
        
        
        self.ui.actionclear.triggered.connect(self.clear_selectedAtoms)

        self.updater=Updater(self)
        self.orbitalType:str='cloud' # 显示轨道的方式，点云(cloud)或箭头(arrow)
        # self.ui.cloudRangeSlider.valueChanged.connect(self.set_cloudRange)
        # self.ui.clearCloudBtn.clicked.connect(lambda:self.currentFile.canvas.clear('cloud'))

        self.files:Dict[str,FileItem]={}
        self.currentFile:FileItem=None # 初始化一个啥都没有的文件
        # self.ui.verticalLayout_canvas.addWidget(self.currentFile.widget) #第一次打开的时候添加组件，之后是替换组件
        
        # self.canvasLayout.addWidget(StartWidget())
        self.init_layout()
        self.orbital=OrbitalWidget(self)
        self.viewLaout.addWidget(self.orbital)

    def init_layout(self):
        """初始化布局"""
        self.fileTab=QHBoxLayout()
        self.ui.fileTab.setLayout(self.fileTab)
        self.canvasLayout=QVBoxLayout()
        self.ui.canvas.setLayout(self.canvasLayout)
        self.viewLaout=QVBoxLayout()
        self.ui.view.setLayout(self.viewLaout)

    def init_menu(self):
        """初始化菜单的命令"""
        self.ui.actionopen.triggered.connect(self.openFile)
        self.ui.actionpiBondOrder.triggered.connect(lambda:self.compute_piOrder('new'))


        self.ui.actionpiSelectOrder.triggered.connect(lambda:self.compute_piOrder('old'))
        self.ui.actionlabel.triggered.connect(self.viewLabel)

    def clear_selectedAtoms(self):
        if self.currentFile is not None:
            self.currentFile.canvas.clearAtoms()

    def command(self):
        """处理命令行输入的内容"""
        opt=self.ui.lineEdit.text()
        res=self.commandLine.run(opt)
        self.addInfo(res)


    def compute_piOrder(self,orderType):
        atoms=self.currentFile.canvas.selectedAtoms
        if len(atoms)==2:
            if orderType=='old':
                computer=piSH.Calculator(self.currentFile.mol)
            if orderType=='new':
                computer=piDM.Calculator(self.currentFile.mol)
            res=computer.calculate(atoms[0],atoms[1])
            orders=res['data']['orders']
            order=res['data']['order']
            # 将orders根据大小进行排序，并删除为0的部分
            orders=sorted(zip(range(len(orders)),orders),key=lambda x:x[1])
            limit=1e-4
            ranges=[r+1 for r,o in orders if o>=limit]
            orbitalNum=len(self.currentFile.mol.O_obts)
            orbitalNum=orbitalNum//2+orbitalNum%2
            oE=1 if self.currentFile.mol.isOpenShell else 2
            if oE==1:
                ranges = [f"α{r}" if r <= orbitalNum else f'β{r-orbitalNum}' for r in ranges]

            orders=[o for r,o in orders if o>=limit]
            self.addLog(f'compute piSelectOrder {atoms[0].idx}-{atoms[1].idx}')
            rangesStrs=[f'{each}' for each in ranges]
            ordersStrs=[f'{each:.4f}' for each in orders]
            self.formPrint([rangesStrs,ordersStrs],eachLength=8,lineNum=10)
            self.addLog(f'{order=:.4f}')
        else:
            self.addLog('compute bond order need two atoms')

    def viewLabel(self):
        """显示或隐藏原子的label"""
        label=self.currentFile.canvas.labels
        visible=label.GetVisibility()
        label.SetVisibility(int(not visible))
        print(label.GetVisibility())
    
    def addLog(self,log:str):
        """输出程序的执行结果"""
        self.ui.log.append(log)

    def openFile(self):
        """打开log/out文件"""
        print('打开文件')
        files=[]
        filePaths,fileTypes=QFileDialog.getOpenFileNames(self,"打开文件",filter='log (*.log);;out (*.out)',dir=self.setting.lastOpenFilePath) # 选择文件名
        for filePath,fileType in zip(filePaths,fileTypes):
            # self.ui.listWidget_files.addItem(filePath)
            # self.files[filePath]=FileItem(filePath=filePath,app=self) # 添加一个文件
            files.append(filePath)
            self.addLog(f'open {filePath}')
            self.setting.lastOpenFilePath=str(Path(filePath).parent)
        if len(files)==0:return
        name=files[-1] # 最后一个文件的名称
        fileItem=FileItem(Path(files[-1]),app=self)
        self.currentFile=fileItem
        self.canvasLayout.addWidget(fileItem)
        self.addTab(files[-1])
        # self.showMol(self.currentFile,self.files[name])
    
    def addTab(self,text):
        """在tabFrame添加一个标签"""
        self.fileTab.addWidget(QLabel(text))
            
    def selectFile(self):
        """选择一个打开的文件,当选择文件名的时候，如果就是当前的文件，则不发生变化，如果不是则取代"""
        file=self.ui.listWidget_files.currentItem().text() # 点前选中的文件
        if file==self.currentFile.filePath: # 当前展示的文件
            return
        print('替换组件',self.currentFile.filePath,file)
        oldFile=self.currentFile
        newFile=self.files[file]
        self.showMol(oldFile,newFile)
        
    def showMol(self,oldFile,newFile):
        """显示指定的分子"""
        print('显示指定文字')
        self.update()

    def selectOrbital(self):
        """选择某个轨道"""
        orbital=self.ui.listWidget_orbitals.currentIndex().row()
        self.currentFile.canvas.selectedOrbital=orbital
        if self.orbitalType=='cloud':
            self.currentFile.canvas.addCloud()
        elif self.orbitalType=='arrow':
            atoms=self.currentFile.canvas.selectedAtoms
            for atom in atoms:
                start=atom.coord
                direction=atom.get_obtWay(orbital)
                name=f'{atom.idx}-{orbital}'
                self.currentFile.canvas.add_arrow(start, direction,name)

    def update(self):
        """更新页面中的内容"""
        ...

    def set_cloudRange(self,e):
        """设置点云范围"""
        self.currentFile.canvas.cloudRange=e/10000
        # print(e)
    
    def on_exit(self):
        for each in self.files.values():
            each.canvas.plotter.Finalize()
    
    def closeEvent(self, event) -> None:
        """退出程序时的回调函数"""
        for each in self.files.values():
            each.canvas.plotter.Finalize()
        return super().closeEvent(event)

    def add_fileItem(self):
        """模仿vscode,每一个可视化的分子文件为一个FileItem"""
            

from .plotter.canvas import Mol as MolActor
from .plotter.canvas import Canvas


class FileItem(QWidget):
    """
    应该是一个tab，里面可以包含各种组件
    """
    def __init__(self,filePath:Path,app:Window,showMol:bool=True) -> None:
        QWidget.__init__(self,parent=None)
        self.app=app
        self.filePath=filePath
        mol=get_reader(filePath).mol
        orbitals=[str(o) for o in mol.orbital_symbols]
        self.app.orbital.set_orbitals(orbitals)
        self.layout=QVBoxLayout()

        self.canvas=Canvas(self.app,mol,self)
        self.layout.addWidget(self.canvas.interactor)
        self.setLayout(self.layout)
        # self.init_mol()
        
    
    def hide_mol(self):
        """隐藏原子"""
        ...
        
    
    def onClick(self):
        print('click')

class viewItem(QWidget):
    def __init__(self):
        QWidget.__init__(self,parent=None)