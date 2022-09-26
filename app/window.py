import sys
import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"
import pyvista as pv

from PySide6.QtWidgets import QApplication,QWidget,QLabel,QMainWindow,QStyleFactory,QFileDialog,QMenu
from PySide6.QtGui import QIcon,QFont
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor, MainWindow

from hfv.plotter.canvas import Canvas
from hfv.obj import Mol
from hfv.calculators import piBondOrder,piSelectOrder
from hfv.readers import Reader
from .commands import Command
from .ui_app import Ui_MainWindow
from .setting import settingManager
from .update import Updater

from typing import *
from pathlib import Path

class Window(MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setting=settingManager()
        self.ui:Ui_MainWindow=Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.canvas.setVisible(False)
        self.commandLine=Command(self)
        self.ui.textLog.setFont(QFont('Courier New'))
        self.ui.lineEdit.returnPressed.connect(self.command)
        
        self.init_menu()

        self.ui.listWidget_files.itemClicked.connect(self.selectFile)
        self.ui.listWidget_orbitals.itemClicked.connect(self.selectOrbital)
        self.files:Dict[str,FileItem]={}
        self.currentFile:FileItem=FileItem("",self,showMol=False) # 初始化一个啥都没有的文件
        self.ui.verticalLayout_canvas.addWidget(self.currentFile.widget) #第一次打开的时候添加组件，之后是替换组件
        self.ui.actionclear.triggered.connect(self.clear_selectedAtoms)

        self.updater=Updater(self)
    
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

    def compute_sigmaOrder(self):
        bond=self.currentFile.canvas.selectedBond
        if bond is not None:
            caler=piBondOrder.Calculator(self.currentFile.mol,orderType='sigma')
            res=caler.calculate(bond)
            orders=res['data']['orders']
            order=res['data']['order']


    def compute_piOrder(self,orderType):
        bond=self.currentFile.canvas.selectedBond
        if bond is not None:
            if orderType=='old':
                computer=piSelectOrder.Caculater(self.currentFile.mol)
            if orderType=='new':
                computer=piBondOrder.Calculator(self.currentFile.mol)
            res=computer.calculate(bond.a1,bond.a2)
            orders=res['data']['orders']
            order=res['data']['order']
            # 将orders根据大小进行排序，并删除为0的部分
            orders=sorted(zip(range(len(orders)),orders),key=lambda x:x[1])
            limit=1e-4
            ranges=[r+1 for r,o in orders if o>=limit]
            orbitalNum=len(self.currentFile.mol.O_orbitals)
            orbitalNum=orbitalNum//2+orbitalNum%2
            # print(ranges,orbitalNum)
            orbitalElectron=2 if self.currentFile.mol.isSplitOrbital else 1
            if orbitalElectron==1:
                ranges = [f"α{r}" if r <= orbitalNum else f'β{r-orbitalNum}' for r in ranges]

            orders=[o for r,o in orders if o>=limit]
            self.addLog(f'compute piSelectOrder {bond.idx}')
            rangesStrs=[f'{each}' for each in ranges]
            ordersStrs=[f'{each:.4f}' for each in orders]
            self.formPrint([rangesStrs,ordersStrs],eachLength=8,lineNum=10)
            self.addLog(f'{order=:.4f}')

    def viewLabel(self):
        """显示或隐藏原子的label"""
        label=self.currentFile.canvas.labels
        visible=label.GetVisibility()
        label.SetVisibility(int(not visible))
        print(label.GetVisibility())

    def formPrint(self,contents:List[List[str]],eachLength:int,lineNum:int):
        """格式化打印列表内容，contents是一个列表，其中的每一项是一个包含字符串的列表，每个字符串列表长度必须相同"""
        logs=[]
        for content in contents:
            logs.append([])
            for i in range(0,len(content),lineNum):
                text=''.join([f'{each}'.rjust(eachLength,' ') for each in content[i:i+lineNum]])
                logs[-1].append(text)
        for i in range(len(logs[0])):
            for log in logs:
                self.addLog(log[i])
            

    def addInfo(self,info:str):
        """输出用户输入命令的处理结果"""
        self.ui.textInfo.append(f'>>> {info}')
    
    def addLog(self,log:str):
        """输出程序的执行结果"""
        self.ui.textLog.append(log)

    def openFile(self):
        """打开log/out文件"""
        filePaths,fileTypes=QFileDialog.getOpenFileNames(self,"打开文件",filter='log (*.log);;out (*.out)',dir=self.setting.lastOpenFilePath) # 选择文件名
        for filePath,fileType in zip(filePaths,fileTypes):
            self.ui.listWidget_files.addItem(filePath)
            self.files[filePath]=FileItem(filePath=filePath,app=self) # 添加一个文件
            self.addLog(f'open {filePath}')
            self.setting.lastOpenFilePath=str(Path(filePath).parent)

        name=list(self.files.keys())[-1] # 最后一个文件的名称
        self.showMol(self.currentFile,self.files[name])
        self.update()
            
        
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
        self.ui.verticalLayout_canvas.replaceWidget(oldFile.widget,newFile.widget)
        oldFile.widget.hide()
        newFile.widget.show()
        self.currentFile=newFile
        self.update()

    def selectOrbital(self):
        """选择某个轨道"""
        orbital=self.ui.listWidget_orbitals.currentIndex().row()
        print(orbital)
        self.currentFile.canvas.selectedOrbital=orbital
        self.currentFile.canvas.addCloud()

    def update(self):
        """更新页面中的内容"""
        # 更新轨道信息
        self.ui.listWidget_orbitals.clear()
        orbitals=self.currentFile.mol.orbitals
        orbitals=[f'{i+1} {o}' for i,o in enumerate(orbitals)]
        self.ui.listWidget_orbitals.addItems(orbitals)
        # 更新点云信息
        clouds=self.currentFile.canvas.clouds
        names=[cloud.name for cloud in clouds]
        self.ui.listWidget_clouds.clear()
        self.ui.listWidget_clouds.addItems(names)

class FileItem:
    def __init__(self,filePath:str,app:Window,showMol:bool=True) -> None:
        self.filePath=filePath
        self.plotter:QtInteractor = QtInteractor(app.ui.canvas)
        self.canvas:Canvas = Canvas(self.plotter,app=app)
        self.widget=self.plotter.interactor
        self.widget.key_press_event=lambda e:print(e)
        if showMol:
            self.init_mol()
        
    def init_mol(self):
        self.mol=Reader(self.filePath).mol
        self.mol.create_bonds()
        self.canvas.add_mol(self.mol)
        self.property:Dict={} # 存储分子在属性栏中显示的内容
        print(self.widget.size())
    
    def onClick(self):
        print('click')

