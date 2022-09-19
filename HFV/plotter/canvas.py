from pyvista import Plotter,Cylinder,Sphere,PolyData,Light
from ..obj import Atom,Bond,Mol
from .materials import atomColor
import numpy as np
from typing import *
from .. import utils
import pyvista as pv
from . import util


class Canvas:
    def __init__(self,plotter:Plotter,app=None) -> None:
        self.plotter=plotter
        
        self.app=app
        self.plotter.enable_mesh_picking(callback=self.onClick,left_clicking=True,show_message=False,\
            style='surface')
        self.balls:List[Ball]=[]
        self.sticks:List[Stick]=[]
        self.clouds:List[Clouds]=[]
        self.selectedBond:Bond=None
        self.selectedAtoms:List[Atom]=[]
        self.selectedOrbital:int=0
    
    def clearAtoms(self):
        self.selectedAtoms.clear()
        self.updateApp()

    def onClick(self,mesh:PolyData):
        print(mesh.name)
        meshType=mesh.name.split('-')[0]
        if meshType=='atom':
            atom=self.get_Obj(mesh.name).atom
            if atom is not None:
                self.selectedAtoms.append(atom)
        elif meshType=='bond':
            bond=self.get_Obj(mesh.name).bond
            if bond is not None:
                self.selectedBond=bond
        self.updateApp()

    def clear(self):
        """清除所有的原子和键"""
        renderer=self.plotter.renderer
        actors=renderer.actors
        for actor in actors:
            if hasattr(actor,'name'):
                print(actor.name)
    
    def get_Obj(self,name):
        for ball in self.balls:
            if ball.name==name:
                return ball
        for stick in self.sticks:
            if stick.name==name:
                return stick
        return None

    def get_actor(self,name:str):
        """根据name获取actor"""
        renderer=self.plotter.renderer
        actors=renderer.actors
        for actor in actors:
            if actor.name==name:
                return actor
        return None

    def add_mol(self,mol:Mol):
        points=[]
        symboLabels=[]
        idxLabels=[]
        atoms=mol.atoms
        for i,atom in enumerate(atoms.values()):
            ball=Ball(atom,self.plotter)
            self.balls.append(ball)
            points.append(atom.coord)
            symboLabels.append(atom.symbol)
            idxLabels.append(atom.idx)
        self.labels=self.plotter.add_point_labels(np.array(points),idxLabels,tolerance=0.1,name='idxLabels')
            
        bonds=mol.bonds
        for bond in bonds.values():
            stick=Stick(bond,self.plotter)
            self.sticks.append(stick)
    
    def addCloud(self):
        if self.selectedAtoms:
            idxs=[str(atom.idx) for atom in self.selectedAtoms]
            name=f'{self.selectedOrbital}-{",".join(idxs)}'
            names=[cloud.name for cloud in self.clouds]
            if name in names: #如果已经存在
                print('this cloud exit')
                self.set_visibleCloud()
                return
            cloud=Clouds(self.selectedAtoms,self)
            self.clouds.append(cloud)
            self.set_visibleCloud()

    def set_visibleCloud(self):
        """设置哪些点云是可见的"""
        idxs=[str(atom.idx) for atom in self.selectedAtoms]
        name=f'{self.selectedOrbital}-{",".join(idxs)}'
        for cloud in self.clouds:
            cloud.setVisible(name)

    def updateApp(self):
        """更新程序界面中的信息"""
        if self.app is None:
            return
        self.app.updater.updateLabel()

class Ball: # 定义球类型
    def __init__(self,atom:Atom,plotter) -> None:
        self.atom=atom
        symbol=atom.symbol
        self.poly=Sphere(center=atom.coord)
        self.name=f'atom-{self.atom.idx}'
        self.poly.name=self.name
        plotter.add_mesh(self.poly,color=atomColor[atom.symbol],smooth_shading=True,name=self.name)
        

class Stick: # 定义棍类型
    def __init__(self,bond:Bond,plotter) -> None:
        self.bond=bond
        center=(bond.a1.coord+bond.a2.coord)/2
        direction=bond.a2.coord-bond.a1.coord
        self.name=f'bond-{self.bond.a1.idx},{self.bond.a2.idx}'
        self.poly=Cylinder(center=center,direction=direction,radius=0.2)
        self.poly.name=self.name
        plotter.add_mesh(self.poly,name=self.name)

class Clouds: #定义点云类型
    def __init__(self,atoms:List[Atom],canvas:Canvas) -> None:
        self.canvas=canvas
        # 不管选择哪几个原子，只需要按照原子序号排序
        idxs=[str(atom.idx) for atom in atoms]
        self.name=f'{self.canvas.selectedOrbital}-{",".join(idxs)}'
        if self.canvas.app is not None:
            self.canvas.app.ui.listWidget_clouds.addItem(self.name)
        self.atoms=atoms
        coords=np.array([atom.coord for atom in atoms])
        self.centerPos=np.mean(coords,axis=0)
        self.radius=np.linalg.norm(np.max(np.abs(coords-self.centerPos),axis=0))+1
        self.positiveCloud=None
        self.negativeCloud=None
        self.gridPoints=utils.get_gridPoints(self.radius,0.1,ball=True)
        self.addCloud()
        
    def createData(self):
        datas=[]
        for atom in self.atoms:
            centerPos=self.centerPos.reshape(3,1)
            aroundPos=self.gridPoints+centerPos
            data=utils.posan_function(
                centerPos=centerPos,
                aroundPos=aroundPos,
                paras=atom.standardBasis,
                ts=atom.pLayersTs(self.canvas.selectedOrbital)
                )
            datas.append(data)
        datas=np.array(datas).sum(axis=0)
        return datas

    def addCloud(self):
        values=self.createData()
        points=self.gridPoints+self.centerPos.reshape(3,-1)
        data=np.concatenate([points,values]).T
        positiveValues,negativeValues=util.splited(data)
        positiveValues=util.limited(positiveValues,0.02)
        negativeValues=util.limited(negativeValues,0.02)

        positiveValues=positiveValues.reshape(-1,4)[:,:-1]
        negativeValues=negativeValues.reshape(-1,4)[:,:-1]

        positivePoints=util.get_borders(positiveValues) # 获取边界点
        negativePoints=util.get_borders(negativeValues)

        positivePoints=np.concatenate([positivePoints,self.centerPos.reshape(1,3)]) #为了使数组不为空，需要添加原点
        negativePoints=np.concatenate([negativePoints,self.centerPos.reshape(1,3)])

        positiveCloud=pv.PolyData(positivePoints)
        negativeCloud=pv.PolyData(negativePoints)

        print('添加点云')
        if len(positiveValues)>0:
            self.positiveCloud=self.canvas.plotter.add_mesh(positiveCloud,color='#c12c1f',opacity=0.5,
                reset_camera=False,name=f'positive-{self.name}',pickable=False)
        if len(negativeValues)>0:
            self.negativeCloud=self.canvas.plotter.add_mesh(negativeCloud,color='#84a729',opacity=0.5,
                reset_camera=False,name=f'negative-{self.name}',pickable=False)

    def setVisible(self,name):
        print(f'{name=},{self.name=}')
        if name==self.name:
            if self.positiveCloud:self.positiveCloud.SetVisibility(True)
            if self.negativeCloud:self.negativeCloud.SetVisibility(True)
        else:
            if self.positiveCloud:self.positiveCloud.SetVisibility(False)
            if self.negativeCloud:self.negativeCloud.SetVisibility(False)

