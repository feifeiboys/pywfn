"""
处理用户在命令行文本框输入的命令
只针对一个分子文件
"""
from typing import *
from . import window
import numpy as np

class Command:

    def __init__(self,app:"window.Window") -> None:
        self.app=app
        self.currentFile:"window.FileItem"
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
        self.currentFile=self.app.currentFile
        if self.currentFile is None:
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
        self.currentFile.canvas.plotter.add_points(np.array(point,dtype=np.float32))
    
    def get_view(self):
        """获取当前场景摄像机视角"""
        camera=self.currentFile.canvas.plotter.renderer.camera
        self.app.addLog(f'{camera.position},{camera.focal_point},{camera.up}',logType='info')
    
    def set_view(self,position,focal,up):
        """设置当前场景摄像机视角"""
        camera=self.currentFile.canvas.plotter.camera
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
        plotter=self.currentFile.canvas.plotter
        path=self.currentFile.filePath
        fileName:str=str(path.parent / path.stem)
        print(fileName)
        if fileType=='png':
            plotter.screenshot(f'{fileName}.png',transparent_background=True)
        elif fileType=='obj':
            plotter.export_obj(f'{fileName}.obj')
        elif fileType in ['svg','eps','ps','pdf','tex']:
            plotter.save_graphic(f'{fileName}.{fileType}')
        self.app.addLog(f'导出成功!! {fileName}')
    
    def export_all(self,fileType):
        for file in self.app.fileItems.values():
            self.currentFile=file
            # path=str(file.filePath)
            # self.app.fileSideTab.show_file(path)
            self.export(fileType)


# from .window import Window,FileItem