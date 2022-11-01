from pyvista import Plotter,Cylinder,Sphere,PolyData,Light
from pywfn.base import Atom,Bond,Mol
import numpy as np
from typing import *
from pywfn import utils
import pyvista as pv
from . import util
from .materials import Elements
import vtk
from pyvistaqt import QtInteractor
elements=Elements()


class Canvas:
    def __init__(self,plotter:QtInteractor,app=None) -> None:
        self.plotter=plotter
        
        self.app=app
        self.plotter.enable_mesh_picking(callback=self.onClick,left_clicking=True,show=False,show_message=False,style='wireframe',line_width=1,color='white')
        self.balls:List[Ball]=[]
        self.sticks:List[Stick]=[]
        self.clouds:List[Clouds]=[]
        self.selectedBond:Bond=None
        self.selectedAtoms:List[Atom]=[]
        self.selectedOrbital:int=0
        self.scene=[] # 除了原子之外的actor都加入到scene中，方便管理
        self.cloudRange:float=0.001
    
    def clearAtoms(self):
        self.selectedAtoms.clear()
        self.updateApp()

    def onClick(self,mesh:PolyData):
        # print(mesh.name)
        meshType=mesh.name.split('-')[0]
        if meshType=='atom':
            atom=self.get_Obj(mesh.name).atom
            actor=self.get_Obj(mesh.name).actor
            prop = actor.GetProperty()
            # print(prop,dir(prop))
            
            if atom is not None:
                if atom not in self.selectedAtoms: # 如果该原子没有被选中
                    self.selectedAtoms.append(atom)
                    prop.SetColor(hex2rgb('#108b96'))
                    prop.SetAmbient(0.5)
                else:
                    hexColor=elements[atom.symbol].color
                    rgbColor=hex2rgb(hexColor)
                    # print(rgbColor)
                    prop.SetColor(rgbColor)
                    prop.SetAmbient(0)
                    index=self.selectedAtoms.index(atom)
                    self.selectedAtoms.pop(index)

                actor.SetProperty(prop)
        self.updateApp()

    def clear(self,actorType):
        """清除所有的原子和键"""
        renderer=self.plotter.renderer
        actors=renderer.actors
        for actor in actors:
            if actor.split('-')[0]==actorType: # 删除指定类型的所有actor
                ...
            print(actor)
            # if hasattr(actor,'name'):
            #     print(actor.name)
    
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
        for i,atom in enumerate(mol.atoms):
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
            if name in names: #如果已经存在,并且显示范围相同
                if len(self.clouds)>=1 and self.clouds[-1].cloudRang==self.cloudRange:
                    print('this cloud exit')
                    self.set_visibleCloud()
                    return
            cloud=Clouds(self.selectedAtoms,self)
            self.clouds.append(cloud)
            if len(self.clouds)>=5: # 最多只能保存五个，要不然太占据内存
                self.clouds.pop(0)
            # self.set_visibleCloud()

    def add_arrow(self,start,direction,name):
        """添加向量箭头"""
        arrow=pv.Arrow(start,direction)
        self.plotter.add_mesh(arrow,name=f'arrow-{name}')

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
        print(atom.coord,elements[symbol].radius)
        self.poly=Sphere(center=atom.coord,radius=elements[symbol].radius)
        self.name=f'atom-{self.atom.idx}'
        self.poly.name=self.name
        self.actor=plotter.add_mesh(self.poly,color=elements[symbol].color,smooth_shading=True,name=self.name)
        

class Stick: # 定义棍类型
    def __init__(self,bond:Bond,plotter) -> None:
        self.bond=bond
        center=(bond.a1.coord+bond.a2.coord)/2
        direction=bond.a2.coord-bond.a1.coord
        self.name=f'bond-{self.bond.a1.idx},{self.bond.a2.idx}'
        self.poly=Cylinder(center=center,direction=direction,radius=0.1)
        self.poly.name=self.name
        plotter.add_mesh(self.poly,name=self.name,pickable=False)


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
        self.cloudRang:float=0.0
        
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
        self.cloudRange=self.canvas.cloudRange
        values=self.createData()
        points=self.gridPoints+self.centerPos.reshape(3,-1)
        data=np.concatenate([points,values]).T
        positiveValues,negativeValues=util.splited(data)
        positiveValues=util.limited(positiveValues,self.canvas.cloudRange)
        negativeValues=util.limited(negativeValues,self.canvas.cloudRange)

        positiveValues=positiveValues.reshape(-1,4)[:,:-1]
        negativeValues=negativeValues.reshape(-1,4)[:,:-1]

        positivePoints=util.get_borders(positiveValues) # 获取边界点
        negativePoints=util.get_borders(negativeValues)

        positivePoints=np.concatenate([positivePoints,self.centerPos.reshape(1,3)]) #为了使数组不为空，需要添加原点
        negativePoints=np.concatenate([negativePoints,self.centerPos.reshape(1,3)])
        print('数据点',len(positivePoints),len(negativeValues))
        positiveCloud=pv.PolyData(positivePoints)
        negativeCloud=pv.PolyData(negativePoints)

        # print('添加点云')
        if len(positiveValues)>0:
            self.positiveCloud=self.canvas.plotter.add_mesh(positiveCloud,color='#c12c1f',opacity=0.5,
                reset_camera=False,name=f'cloud-positive-{self.name}',pickable=False)
        if len(negativeValues)>0:
            self.negativeCloud=self.canvas.plotter.add_mesh(negativeCloud,color='#84a729',opacity=0.5,
                reset_camera=False,name=f'cloud-negative-{self.name}',pickable=False)

    def setVisible(self,name):
        # print(f'{name=},{self.name=}')
        if name==self.name:
            if self.positiveCloud:self.positiveCloud.SetVisibility(True)
            if self.negativeCloud:self.negativeCloud.SetVisibility(True)
        else:
            if self.positiveCloud:self.positiveCloud.SetVisibility(False)
            if self.negativeCloud:self.negativeCloud.SetVisibility(False)


def hex2rgb(hexcolor:str):
    '''HEX转RGB'''
    hexcolor=hexcolor.replace('#', '')
    hexcolor = int(hexcolor, base=16)
    rgb = (hexcolor >> 16) & 0xff , (hexcolor >> 8) & 0xff , hexcolor & 0xff 
    return rgb[0]/255,rgb[1]/255,rgb[2]/255

def rgb(r,g,b):
    return r/255,g/255,b/255