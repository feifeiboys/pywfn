"""
处理用户在命令行文本框输入的命令
只针对一个分子文件
"""
from typing import *
from . import window
import numpy as np
from pathlib import Path

class Command:

    def __init__(self,app:"window.Window") -> None:
        self.app=app
        self.molView:"window.MolView"
        self.historys=[] # 记录命令历史
        self.historyIdx=None
    
    def get_history(self,way):
        """获取历史指令"""
        if len(self.historys)==0:return ''
        if way=='up' and self.historyIdx>0:
            self.historyIdx-=1
        elif way=='down':
            if self.historyIdx<len(self.historys)-1:
                self.historyIdx+=1
            else:
                return ''
        return self.historys[self.historyIdx]
        
    def run(self,opt:str):
        self.molView=self.app.molView
        if self.app.molView.canvas.mols is None:
            self.app.addLog('尚未打开任何文件!')
            return
        try: # 尝试执行指令
            eval(f'self.{opt}')
            self.historys.append(opt)
            self.historyIdx=len(self.historys)
            self.app.ui.cmdInput.clear()
        except:
            self.app.addLog('命令执行失败')
            eval(f'self.{opt}')
    
    def add_point(self,point:List[float]):
        if len(point)!=3:
            self.app.addLog('坐标必须为三个数')
            return
        self.molView.canvas.plotter.add_points(np.array(point,dtype=np.float32))
    
    def get_view(self):
        """获取当前场景摄像机视角"""
        camera=self.molView.canvas.plotter.renderer.camera
        self.app.addLog(f'{camera.position},{camera.focal_point},{camera.up}',logType='info')
    
    def set_view(self,position,focal,up):
        """设置当前场景摄像机视角"""
        camera=self.molView.canvas.plotter.camera
        camera.position=position
        camera.focal=focal
        camera.up=up
    
    def set_view_all(self,position,focal,up):
        for file in self.app.fileItems.values():
            camera=file.canvas.plotter.camera
            camera.position=position
            camera.focal=focal
            camera.up=up
    
    def export(self,fileType):
        plotter=self.molView.canvas.plotter
        path=Path(self.molView.now_path)
        fileName:str=str(path.parent / path.stem)
        if fileType=='png':
            plotter.screenshot(f'{fileName}.png',transparent_background=False)
        elif fileType=='obj':
            plotter.export_obj(f'{fileName}.obj')
        elif fileType in ['svg','eps','ps','pdf','tex']:
            plotter.save_graphic(f'{fileName}.{fileType}')
        self.app.addLog(f'导出成功!! {fileName}')
    
    def export_all(self,fileType):
        molIDs=self.molView.canvas.mols.keys()
        for molID in molIDs:
            self.molView.on_show(molID)
            print(f'显示分子{molID}')
            self.export(fileType)
    
    def render_cloud(self,obt:int,atoms:List[int],molID:str=None):
        if len(atoms)==0:
            atoms=[atom.idx-1 for atom in self.molView.now_mol.atoms] #索引从0开始
        else:
            atoms=[atom-1 for atom in atoms]
        if molID is None:molID=self.molView.canvas.molID
        self.molView.canvas.show_cloud(obt=obt-1,atoms=atoms,molID=molID)
    
    def render_cloud_all(self,obt:int,atoms:List[int]):
        molIDs=self.molView.canvas.mols.keys()
        print(molIDs)
        for molID in molIDs:
            # print(molID)
            self.render_cloud(obt,atoms,molID)

# from .window import Window,FileItem