import sys
import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"
import pyvista as pv

from PySide6.QtWidgets import QFileDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QLayout
from PySide6.QtGui import QIcon,QFont,QColor
from PySide6.QtCore import Qt,QObject,QEvent,QThread
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
from .threads import Test
from . import threads
from . import utils


from .pages.setting import SettingWidget
from .pages.start import StartWidget
from .pages.orbital import OrbitalWidget
from .pages.fileSideTab import FileSideTabWidget

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
        
        self.init_layout()
        self.init_pages()
        self.init_funs()
        self.molView=MolView(app=self)
        self.threads:Dict[str,QThread]={} #存储线程，防止直接死掉


    def init_pages(self):
        """初始化一些子页面"""
        self.settingPage=SettingWidget(self)
        self.fileSideTab=FileSideTabWidget(self)
        self.obtSideTab=OrbitalWidget(self)
        # self.viewLaout.addWidget(self.fileSideTab)
        self.set_layoutWidget(self.viewLaout,self.fileSideTab)

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
        self.ui.actionclearCloud.triggered.connect(lambda:self.molView.canvas.hide_cloud(names=[]))
        self.ui.actionpiDH.triggered.connect(lambda:self.caler_bondOrder('piDH'))
        self.ui.actionpiDM.triggered.connect(lambda:self.caler_bondOrder('piDM'))
        self.ui.actionpiSH.triggered.connect(lambda:self.caler_bondOrder('piSH'))
        self.ui.actionpiSM.triggered.connect(lambda:self.caler_bondOrder('piSM'))
        self.ui.actionMayer.triggered.connect(lambda:self.caler_bondOrder('Mayer'))

        self.ui.actionMullikenCharge.triggered.connect(lambda:self.claer_atomProp('MullikenCharge'))
        self.ui.actionpiElectron.triggered.connect(lambda:self.claer_atomProp('piElectron'))
        self.ui.actionfreeValence.triggered.connect(lambda:self.claer_atomProp('freeValence'))
        self.ui.actionresetAtomColor.triggered.connect(lambda:self.molView.canvas.reset_color())
        self.ui.actionclear.triggered.connect(self.clear_selectedAtoms)

    def init_funs(self):
        """初始化组件函数绑定"""
        self.ui.cmdInput.returnPressed.connect(self.cmdRun)
        self.ui.cmdInput.installEventFilter(self)
        self.ui.iconFiles.mousePressEvent=lambda e:self.set_layoutWidget(self.viewLaout,self.fileSideTab)
        self.ui.iconOrbital.mousePressEvent=lambda e:self.set_layoutWidget(self.viewLaout,self.obtSideTab)
    
    # 事件过滤器
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched.objectName()=='cmdInput':
            if event.type()==QEvent.KeyPress:
                if event.key()==Qt.Key_Up:
                    opt=self.commandLine.get_history('up')
                    self.ui.cmdInput.setText(opt)
                elif event.key()==Qt.Key_Down:
                    opt=self.commandLine.get_history('down')
                    self.ui.cmdInput.setText(opt)
        return super().eventFilter(watched, event)

    def set_layoutWidget(self,layout:QLayout,widget:QWidget):
        """设置在某个layout内显示指定的widget"""
        count=layout.count()
        if count==0:
            layout.addWidget(widget)
        elif count==1:
            oldWidget=layout.itemAt(0).widget() #当前的组件
            oldWidget.close()
            layout.replaceWidget(oldWidget,widget)
            widget.show()

    def clear_selectedAtoms(self):
        if self.molView is not None:
            self.molView.canvas.clearAtoms()
            
    def cmdRun(self):
        """处理命令行输入的内容"""
        opt=self.ui.cmdInput.text()
        self.commandLine.run(opt)

    def viewLabel(self):
        """显示或隐藏原子的label"""
        label=self.molView.canvas.labels
        visible=label.GetVisibility()
        label.SetVisibility(int(not visible))
    
    def addLog(self,log:str,logType='base',end='\n'):
        """输出程序的执行结果"""
        colors={'base':'#181a17','info':'#4338ba'}
        # self.ui.log.insertHtml(f'<p> >>> <span style="color:{colors[logType]}">{log}</span><br></p>')
        self.ui.log.append(f'>>>\n{log}')

    def openFile(self):
        """打开log/out文件"""
        filePaths,fileTypes=QFileDialog.getOpenFileNames(self,"打开文件",filter='log (*.log);;out (*.out)',dir=self.setting.lastOpenFilePath) # 选择文件名
        if len(filePaths)==0:return
        name=utils.randName()
        self.threads[name]=threads.AddMol(self)
        self.threads[name].paths=filePaths
        self.threads[name].start()
        self.setting.lastOpenFilePath=str(Path(filePaths[-1]).parent)
                   
    def addTab(self,text):
        """在tabFrame添加一个标签"""
        self.fileTab.addWidget(QLabel(text))
            
    def selectFile(self):
        """选择一个打开的文件,当选择文件名的时候，如果就是当前的文件，则不发生变化，如果不是则取代"""
        file=self.ui.listWidget_files.currentItem().text() # 点前选中的文件
        if file==self.molView.filePath: # 当前展示的文件
            return
        print('替换组件',self.molView.filePath,file)
        oldFile=self.molView
        newFile=self.files[file]
        self.showMol(oldFile,newFile)
        
    def showMol(self,oldFile,newFile):
        """显示指定的分子"""
        print('显示指定文字')
        self.update()

    def selectOrbital(self):
        """选择某个轨道"""
        orbital=self.ui.listWidget_orbitals.currentIndex().row()
        self.molView.canvas.selectedOrbital=orbital
        if self.orbitalType=='cloud':
            self.molView.canvas.addCloud()
        elif self.orbitalType=='arrow':
            atoms=self.molView.canvas.selectedAtoms
            for atom in atoms:
                start=atom.coord
                direction=atom.get_obtWay(orbital)
                name=f'{atom.idx}-{orbital}'
                self.molView.canvas.add_arrow(start, direction,name)

    def update(self):
        """更新页面中的内容"""
        ...

    def set_cloudRange(self,e):
        """设置点云范围"""
        self.molView.canvas.cloudRange=e/10000
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
        atoms=self.molView.canvas.selectedAtoms
        if len(atoms)!=2:return
        atoms=[int(atom.split('-')[1]) for atom in atoms]
        mol=self.molView.now_mol
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
        # res=caler.calculate(idx1,idx2)
        resStr=caler.resStr(idx1,idx2)
        self.addLog(f'\n{resStr}')
    
    def claer_atomProp(self,name): # 计算原子性质
        mol=self.molView.now_mol
        if name=='MullikenCharge': # 计算mulliken电荷分布
            caler=mullikenCharge.Calculator(mol)
            values=caler.calculate()
            idxs=list(range(len(self.molView.now_mol.atoms)))
            idxs=[idx+1 for idx in idxs]
            self.molView.canvas.set_colors(idxs,values)
            resStr=caler.resStr()
            

        elif name=='piElectron': # 计算π电子分布
            atoms=mol.atoms
            caler=piElectron.Calculator(mol)
            values=caler.calculate()
            idxs=list(range(len(self.molView.now_mol.atoms)))
            idxs=[idx+1 for idx in idxs]
            self.molView.canvas.add_arrows_(idxs,values)
            resStr=caler.resStr()
            # pi电子计算的是所有非H原子的
            points=self.molView.now_mol.coords
            labels=[f'{value:.4f}' for value in values]
            self.molView.canvas.add_labels('piElectron',points,labels)


        elif name=='freeValence':
            atoms=self.molView.canvas.selectedAtoms
            if len(atoms)!=1:return
            atoms=[int(atom.split('-')[1]) for atom in atoms]
            idx=int(atoms[0])
            caler=freeValence.Calculator(mol)
            # res=caler.calculate(atom)
            resStr=caler.resStr(idx)
        
        self.addLog(resStr)
    
    def showMessage(self,msg:str):
        """在状态栏显示文本信息"""
        self.statusBar().showMessage(msg)
    
            
from .plotter.canvas import Mol as MolActor
from .plotter.canvas import Canvas

class MolView(QWidget):
    """
    应该是一个tab，里面可以包含各种组件
    
    """
    def __init__(self,app:Window) -> None:
        QWidget.__init__(self,parent=None)
        self.app=app
        self.showObtIdx:int=None
        self.canvas=Canvas(self.app,self)
        self.mols:Dict[str:Mol]={} #分子ID与分子的对应关系
        self.paths:Dict[str,str]={} #分子ID与文件路径的对应关系
        self.app.canvasLayout.addWidget(self.canvas.interactor)
    
    def add_mol(self,path:str):
        self.app.addLog(f'open {path}')
        mol=get_reader(Path(path)).mol
        molID=str(id(mol))
        self.app.fileSideTab.add_file(path,molID)
        self.canvas.add_mol(molID=molID,mol=mol)
        self.mols[molID]=mol
        self.paths[molID]=path
        self.on_show(molID)
    
    def on_show(self,molID:str):
        self.canvas.show_mol(molID)
        self.show_obts()
        self.app.obtSideTab.on_show()
        

    def show_obts(self):
        orbitals=self.now_mol.obtStr
        self.app.obtSideTab.set_orbitals(orbitals)
    
    @property
    def now_mol(self)->Mol:
        """获取当前显示的分子"""
        molID=self.canvas.molID
        return self.mols[molID]

    @property
    def now_path(self)->str:
        molID=self.canvas.molID
        return self.paths[molID]

    
    def hide_mol(self):
        """隐藏原子"""
        ...
        
    def onClick(self):
        print('click')

    def set_atomColor(self,idxs,values):
        self.canvas.set_colors(idxs,values)
    
    def __repr__(self) -> str:
        return self.filePath
    
    def __str__(self) -> str:
        return self.filePath

class viewItem(QWidget):
    def __init__(self):
        QWidget.__init__(self,parent=None)