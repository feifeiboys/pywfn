from pyvista import Plotter,Cylinder,Sphere,PolyData,Light
from pywfn.base import Atom,Bond,Mol
import numpy as np
from typing import *
from pywfn import utils
import pyvista as pv
from . import utils
from .materials import Elements
import vtk
from pyvistaqt import QtInteractor
from . import utils
elements=Elements()


class Canvas(QtInteractor):
    """继承自plotter"""
    def __init__(self,parent,app=None) -> None:
        super().__init__(parent=parent)        
        self.app=app
        self.plotter=self.interactor
        self.plotter.enable_mesh_picking(callback=self.onClick,left_clicking=True,show=False,show_message=False,\
            style='wireframe',line_width=1,color='white')
        self.mols:List[Mol]=[]
        self.scene=[] # 除了原子之外的actor都加入到scene中，方便管理
        self.cloudRange:float=0.001
        self.selectedAtoms=[]
    
    def onClick(self,mesh):
        for mol in self.mols:
            mol.onClick(mesh)

    
class Mol:
    """分子对象，包含原子对象，键对象和点云对象"""
    def __init__(self,plotter:QtInteractor) -> None:
        self.plotter=plotter
        self.actors=[] #存储所有要显示的对象
        self.atomActors={}
        self.selectedAtoms=[]
    
    def add_atom(self,coord,symbol:str,idx:int):
        poly=Sphere(center=coord,radius=elements[symbol].radius)
        name=f'{symbol}-{idx}'
        poly.name=name
        actor=self.plotter.add_mesh(poly,color=elements[symbol].color,smooth_shading=True,name=name)
        self.atomActors[name]=actor
        self.actors.append(actor)
        
    
    def add_bond(self,coord1,coord2,name:str):
        poly=Cylinder(center=(coord1+coord2)/2,direction=coord2-coord1,radius=0.1)
        actor=self.plotter.add_mesh(poly,name=name,pickable=False)
        self.actors.append(actor)

    def add_cloud(self,points,color:str,name:str):
        cloud=pv.PolyData(points)
        if len(points)>0:
            actor=self.plotter.add_mesh(cloud,color=color,opacity=0.5,
                reset_camera=False,name=f'cloud-positive-{name}',pickable=False)
            self.actors.append(actor)

    def onClick(self,mesh:PolyData): #使选中的原子改变颜色
        if not hasattr(mesh,'name'):return
        name:str=mesh.name
        symbol,idx=name.split('-')
        actor=self.atomActors[mesh.name]
        prop = actor.GetProperty()
        if name not in self.selectedAtoms: # 如果该原子没有被选中
            self.selectedAtoms.append(name)
            prop.SetColor(utils.hex2rgb('#108b96'))
            prop.SetAmbient(0.5)
        else:
            hexColor=elements[symbol].color
            rgbColor=utils.hex2rgb(hexColor)
            prop.SetColor(rgbColor)
            prop.SetAmbient(0)
            index=self.selectedAtoms.index(name)
            self.selectedAtoms.pop(index)
            actor.SetProperty(prop)