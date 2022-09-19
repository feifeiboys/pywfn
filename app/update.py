# 更新程序页面中的信息
import numpy as np
from hfv import utils


class Updater:
    def __init__(self,app:"Window"):
        self.app=app
    def updateLabel(self):
        selectedAtoms=self.app.currentFile.canvas.selectedAtoms
        message=f'atoms {[atom.idx for atom in selectedAtoms]}'
        if len(selectedAtoms)==2: # 添加键长信息
            a1,a2=selectedAtoms
            bondLength=np.linalg.norm(a2.coord-a1.coord)
            message+=f',{bondLength:.4f}Å'
        elif len(selectedAtoms)==3: # 添加键角信息
            a1,a2,a3=selectedAtoms
            angle=utils.vector_angle(a1.coord-a2.coord, a3.coord-a2.coord)/np.pi*180
            print(angle)
            message+=f',{angle:.4f}°'
        self.app.ui.label.setText(message)



# from .window import Window