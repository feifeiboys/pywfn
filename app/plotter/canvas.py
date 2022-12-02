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
from ..window import Mol
elements=Elements()


class Canvas(QtInteractor):
    """继承自plotter"""
    def __init__(self,app,mol:Mol,parent) -> None:
        """每个canvas都对应一个分子"""
        super().__init__(parent=parent)        
        self.app=app
        self.mol=mol
        self.plotter=self.interactor
        self.plotter.enable_mesh_picking(callback=self.onClick,left_clicking=True,show=False,show_message=False,\
            style='wireframe',line_width=1,color='white')
        self.mols:List[Mol]=[]
        self.scene=[] # 除了原子之外的actor都加入到scene中，方便管理
        self.cloudRange:float=0.001
        self.selectedAtoms:List[str]=[]
        self.actors=[] #存储所有要显示的对象
        self.atomActors={}

        for atom in self.mol.atoms:
            self.add_atom(atom.coord,atom.symbol,atom.idx)
        for bond in self.mol.bonds:
            a1,a2=bond.a1,bond.a2
            self.add_bond(a1.coord,a2.coord,bond.idx)
    
    def onClick(self,mesh):
        for mol in self.mols:
            mol.onClick(mesh)
        
    
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

    def show_cloud(self,obt:int):
        """
        显示指定原子的轨道
        """
        if len(self.selectedAtoms)==0:
            print('尚未选择原子')
            return
        # 根据原子计算点云应该存在的位置
        print(self.selectedAtoms)
        atoms=[int(a.split('-')[1])-1 for a in self.selectedAtoms]
        atoms.sort()
        atomStr=','.join([str(a) for a in atoms])
        name=f'{atomStr}-{obt}'
        coords=self.mol.coords[atoms,:]
        minX,minY,minZ=np.min(coords,axis=0)
        maxX,maxY,maxZ=np.max(coords,axis=0)
        step=0.1
        pos=[]
        for x in np.arange(minX-1,maxX+1,step):
            for y in np.arange(minY-1,maxY+1,step):
                for z in np.arange(minZ-1,maxZ+1,step):
                    pos.append([x,y,z])
        pos=np.array(pos)
        values=np.zeros(len(pos))
        print(values.shape,pos.shape)
        for i in atoms:
            atom=self.mol.atoms[i]
            values+=atom.get_cloud(pos-atom.coord,obt)
        # P:positive，N:negative
        print('values范围',values.min(),values.max())
        idxsP=np.argwhere(values>0.2).flatten()
        idxsN=np.argwhere(values<-0.2).flatten()
        posP=pos.copy()[idxsP]
        posN=pos.copy()[idxsN]
        self.add_cloud(posP,'red',f'cloud-P-{name}')
        self.add_cloud(posN,'blue',f'cloud-N-{name}')


    def add_cloud(self,points,color:str,name:str):
        if len(points)>0:
            cloud=pv.PolyData(points)
            actor=self.plotter.add_mesh(cloud,color=color,opacity=0.5,
                reset_camera=False,name=name,pickable=False)
            self.actors.append(actor)
        else:
            print('没有点')

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