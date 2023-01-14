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
from pywfn.bondorder import piDH,piSH,piDM,piSM,mayer
from pywfn.atomprop import mullikenCharge,piElectron,freeValence
from pywfn.readers import get_reader

from .plotter.canvas import Canvas
from .commands import Command
from .ui_app import Ui_MainWindow
from .setting import settingManager

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
        
        self.init_menu()
        
        self.orbitalType:str='cloud' # 显示轨道的方式，点云(cloud)或箭头(arrow)
        
        self.files:Dict[str,FileItem]={}
        self.currentFile:FileItem=None # 初始化一个啥都没有的文件
        
        self.init_layout()
        self.orbital=OrbitalWidget(self)
        self.viewLaout.addWidget(self.orbital)

        self.init_pages()

    def init_pages(self):
        """初始化一些子页面"""
        self.settingPage=SettingWidget()

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
        self.ui.actionsetting.triggered.connect(lambda:self.settingPage.show())
        self.ui.actionatomLabels.triggered.connect(self.viewLabel)
        self.ui.actionclearCloud.triggered.connect(lambda:self.currentFile.canvas.hide_cloud(names=[]))
        self.ui.actionpiDH.triggered.connect(lambda:self.caler_bondOrder('piDH'))
        self.ui.actionpiDM.triggered.connect(lambda:self.caler_bondOrder('piDM'))
        self.ui.actionpiSH.triggered.connect(lambda:self.caler_bondOrder('piSH'))
        self.ui.actionpiSM.triggered.connect(lambda:self.caler_bondOrder('piSM'))
        self.ui.actionMayer.triggered.connect(lambda:self.caler_bondOrder('Mayer'))

        self.ui.actionMullikenCharge.triggered.connect(lambda:self.claer_atomProp('MullikenCharge'))
        self.ui.actionpiElectron.triggered.connect(lambda:self.claer_atomProp('piElectron'))
        self.ui.actionfreeValence.triggered.connect(lambda:self.claer_atomProp('freeValence'))
        self.ui.actionresetAtomColor.triggered.connect(lambda:self.currentFile.canvas.reset_color())
        self.ui.actionclear.triggered.connect(self.clear_selectedAtoms)
    def clear_selectedAtoms(self):
        if self.currentFile is not None:
            self.currentFile.canvas.clearAtoms()
            

    def command(self):
        """处理命令行输入的内容"""
        opt=self.ui.lineEdit.text()
        res=self.commandLine.run(opt)
        self.addInfo(res)

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

    def caler_bondOrder(self,name): # 计算键性质
        atoms=self.currentFile.canvas.selectedAtoms
        if len(atoms)!=2:return
        atoms=[int(atom.split('-')[1]) for atom in atoms]
        mol=self.currentFile.mol
        if name=='piDH':
            caler=piDH.Calculator(mol)
        elif name=='piSH':
            caler=piSH.Calculator(mol)
        elif name=='piDM':
            caler=piDM.Calculator(mol)
        elif name=='piSM':
            caler=piSM.Calculator(mol)
        elif name=='Mayer':
            caler=mayer.Calculator(mol)
        idx1,idx2=atoms
        res=caler.calculate(mol.atom(idx1), mol.atom(idx2))
        self.addLog(f'{res}')
    
    def claer_atomProp(self,name): # 计算原子性质
        mol=self.currentFile.mol
        if name=='MullikenCharge': # 计算mulliken电荷分布
            caler=mullikenCharge.Calculator(mol)
            
            values=caler.calculate()
            idxs=list(range(len(self.currentFile.mol.atoms)))
            idxs=[idx+1 for idx in idxs]
            self.currentFile.canvas.set_colors(idxs,values)
            resStr=caler.resStr()
            

        elif name=='piElectron': # 计算π电子分布
            atoms=mol.atoms
            caler=piElectron.Calculator(mol)
            values=caler.calculate()
            idxs=list(range(len(self.currentFile.mol.atoms)))
            idxs=[idx+1 for idx in idxs]
            self.currentFile.canvas.add_arrows_(idxs,values)
            resStr=caler.resStr()


        elif name=='freeValence':
            atoms=self.currentFile.canvas.selectedAtoms
            if len(atoms)!=1:return
            atoms=[int(atom.split('-')[1]) for atom in atoms]
            atom=mol.atom(int(atoms[0]))
            caler=freeValence.Calculator(mol)
            # res=caler.calculate(atom)
            resStr=caler.resStr(atom)
        
        self.addLog(resStr)
    
    def showMessage(self,msg:str):
        """在状态栏显示文本信息"""
        self.statusBar().showMessage(msg)
    
            
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
        self.mol=mol=get_reader(filePath).mol
        orbitals=[str(o) for o in mol.orbital_symbols]
        self.app.orbital.set_orbitals(orbitals)
        self.layout=QHBoxLayout()

        self.canvas=Canvas(self.app,mol,self)
        self.layout.addWidget(self.canvas.interactor)
        self.setLayout(self.layout)
        # self.init_mol()
        
    
    def hide_mol(self):
        """隐藏原子"""
        ...
        
    def onClick(self):
        print('click')

    def set_atomColor(self,idxs,values):
        self.canvas.set_colors(idxs,values)

class viewItem(QWidget):
    def __init__(self):
        QWidget.__init__(self,parent=None)