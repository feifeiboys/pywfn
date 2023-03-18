import sys
import os
import PySide6
dirname = os.path.dirname(PySide6.__file__) 
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
os.environ["QT_API"] = "pyside6"
import pyvista as pv

from PySide6.QtWidgets import QFileDialog,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QLayout,QMenu,QApplication
from PySide6.QtGui import QIcon,QFont,QColor,QAction,QKeyEvent,QMouseEvent
from PySide6.QtCore import Qt,QObject,QEvent,QThread,QThreadPool
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
from . import threads
from . import utils
from . import signals


from .pages.color import ColorPage
from .pages.start import StartPage

from .sideTabs.orbital import OrbitalWidget
from .sideTabs.files import FileSideTabWidget
from .sideTabs.scene import SceneSideTabWidget

class Window(MainWindow):
    def __init__(self,app:QApplication) -> None:
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
        
        # app.installEventFilter(self)qianru

    def init_pages(self):
        """初始化一些子页面"""
        self.colorPage=ColorPage(self)
        self.startPage=StartPage(self)

        self.fileSideTab=FileSideTabWidget(self)
        self.obtSideTab=OrbitalWidget(self)
        self.sceneSideTab=SceneSideTabWidget(self)
        # self.viewLaout.addWidget(self.fileSideTab)
        self.set_layoutWidget(self.viewLaout,self.fileSideTab)

    def init_layout(self):
        """初始化布局"""
        self.fileTab=QHBoxLayout()
        self.ui.pageTabs.setLayout(self.fileTab)

        self.pageLayout=QVBoxLayout()
        self.pageLayout.setContentsMargins(0,0,0,0)
        self.ui.canvas.setLayout(self.pageLayout)

        self.viewLaout=QVBoxLayout()
        self.ui.view.setLayout(self.viewLaout)

    def init_menu(self):
        """初始化菜单的命令"""
        # file
        self.ui.actionopen.triggered.connect(self.openFile)
        self.ui.actionsetting.triggered.connect(lambda:self.settingPage.show())
        self.ui.actionatomLabels.triggered.connect(lambda:self.molView.canvas.show_label())
        self.ui.actionclearCloud.triggered.connect(lambda:self.molView.canvas.hide_cloud(names=[]))
        # compute
        self.ui.actionpiDH.triggered.connect(lambda:self.caler_bondOrder('piDH'))
        self.ui.actionpiDM.triggered.connect(lambda:self.caler_bondOrder('piDM'))
        self.ui.actionpiSH.triggered.connect(lambda:self.caler_bondOrder('piSH'))
        self.ui.actionpiSM.triggered.connect(lambda:self.caler_bondOrder('piSM'))
        self.ui.actionMayer.triggered.connect(lambda:self.caler_bondOrder('Mayer'))

        self.ui.actionMullikenCharge.triggered.connect(lambda:self.claer_atomProp('MullikenCharge'))
        self.ui.actionpiElectron.triggered.connect(lambda:self.claer_atomProp('piElectron'))
        self.ui.actionfreeValence.triggered.connect(lambda:self.claer_atomProp('freeValence'))
        # view
        self.ui.actionresetAtomColor.triggered.connect(lambda:self.molView.canvas.reset_color())
        # select
        self.ui.actionclear.triggered.connect(self.clear_selectedAtoms)
        # setting
        self.ui.actioncolor.triggered.connect(lambda:self.colorPage.show())

    def init_funs(self):
        """初始化组件函数绑定"""
        self.ui.cmdInput.returnPressed.connect(self.cmdRun)
        self.ui.cmdInput.installEventFilter(self) #要绑定一个类，这个类要是QObject的子类，而且要有eventFilter函数
        self.ui.iconFiles.mousePressEvent=lambda e:self.set_layoutWidget(self.viewLaout,self.fileSideTab)
        self.ui.iconOrbital.mousePressEvent=lambda e:self.set_layoutWidget(self.viewLaout,self.obtSideTab)
        self.ui.iconScene.mousePressEvent=lambda e:self.set_layoutWidget(self.viewLaout,self.sceneSideTab)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key()==Qt.Key_Up:
                opt=self.commandLine.get_history('up')
                self.ui.cmdInput.setText(opt)
            elif event.key()==Qt.Key_Down:
                opt=self.commandLine.get_history('down')
                self.ui.cmdInput.setText(opt)
        return False
    

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
    
    def addLog(self,log:str,logType='base',end='\n'):
        """输出程序的执行结果"""
        colors={'base':'#181a17','info':'#4338ba'}
        # self.ui.log.insertHtml(f'<p> >>> <span style="color:{colors[logType]}">{log}</span><br></p>')
        self.ui.log.append(f'>>>\n{log}')

    def openFile(self):
        """打开log/out文件"""
        filePaths,fileTypes=QFileDialog.getOpenFileNames(self,"打开文件",filter='log (*.log);;out (*.out)',dir=self.setting.lastOpenFilePath) # 选择文件名
        
        if len(filePaths)==0:return
        
        self.threadpool=QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        
        for path in filePaths:
            t=threads.AddMol(self,path)
            t.signal=signals.OpenFile()
            t.signal.sig.connect(self.molView.add_mol)
            t.setAutoDelete(True)
            self.threadpool.start(t)
        self.threadpool.waitForDone()
        print('文件读取完成')
            
        # self.t=threads.AddMol(self,filePaths)            
        # self.t._signal.connect(self.molView.add_mol)
        # self.t.start()
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
        self.molView.canvas.close()
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


from collections import namedtuple
File=namedtuple('File',['path','molID','mol'])
class MolView(QWidget):
    """
    应该是一个tab，里面可以包含各种组件
    
    """
    def __init__(self,app:Window) -> None:
        QWidget.__init__(self,parent=None)
        self.app=app
        self.showObtIdx:int=None
        self.canvas=Canvas(self.app,self)
        self.files:List[File]=[]
        self.app.pageLayout.addWidget(self.canvas)
        self.canvas.installEventFilter(self)
        self.R_Menu()
        
    def get_file(self,prop,value):
        """根据属性值返回文件"""
        for file in self.files:
            if getattr(file,prop)==value:
                return file
    
    def add_mol(self,path:str,mol:Mol):
        self.app.addLog(f'open {path}')
        # mol=get_reader(Path(path)).mol
        molID=str(id(mol))
        self.app.fileSideTab.add_file(path,molID)
        self.canvas.add_mol(molID=molID,mol=mol)
        self.files.append(File(path,molID,mol))

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
        file=self.get_file('molID',molID)
        return file.mol

    @property
    def now_path(self)->str:
        molID=self.canvas.molID
        file=self.get_file('molID',molID)
        return file.path

    def hide_mol(self):
        """隐藏原子"""
        ...

    def set_atomColor(self,idxs,values):
        self.canvas.set_colors(idxs,values)

    def R_Menu(self):
        """定义右键菜单"""
        self.r_menu=QMenu()

        act=QAction("相位反转",self)
        act.triggered.connect(self.canvas.reverse_cloud)
        self.r_menu.addAction(act)

        act=QAction("相位恢复",self)
        act.triggered.connect(lambda :self.canvas.reverse_cloud(reset=True))
        self.r_menu.addAction(act)

        act=QAction("删除轨道",self)
        act.triggered.connect(self.canvas.remove_cloud)
        self.r_menu.addAction(act)

        act=QAction("清空轨道",self)
        act.triggered.connect(lambda :self.canvas.remove_cloud(clear=True))
        self.r_menu.addAction(act)
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # print(event.type(),type(event.type()))
        if event.type()==QEvent.MouseButtonPress:
            if event.button()==Qt.RightButton:
                self.r_menu.exec(event.globalPos())
        return super().eventFilter(watched, event)
    
    def remove_mol(self,molID:str=None):
        """
        删除一个分子，需要删除的东西有很多
        1.画布中的所有该分子的actor要删除
        2.文件列表中该文件要删除
        """
        if molID==None:molID=self.canvas.molID
        self.canvas.remove_mol(molID)
