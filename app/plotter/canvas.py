"""
一个canvas里面有一个分子，其实就是原子和键
原子的名字的格式为：symbol-idx
"""

from pyvista import Plotter,Cylinder,Sphere,PolyData,Light,Actor,Property,Color
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
from .. import window
elements=Elements()



class Canvas(QtInteractor):
    """继承自plotter"""
    def __init__(self,app:"window.Window",mol:Mol,parent) -> None:
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
        self.isoValue=0.06
        self.borderValue=4
        self.add_atoms()
        self.add_bonds()
        self.labels={} #标签会有很多个
        self.add_labels()
        self.plotter.show_axes()
        
    def add_atoms(self):
        for atom in self.mol.atoms:
            poly=Sphere(center=atom.coord,radius=elements[atom.symbol].radius)
            name=f'{atom.symbol}-{atom.idx}'
            setattr(poly,'name',name) #为poly添加name属性，只有能够被点击的物体才设置name，以便与场景中的actor对照
            self.plotter.add_mesh(poly,color=elements[atom.symbol].color,smooth_shading=True,name=name)

    def add_bonds(self):
        for bond in self.mol.bonds:
            a1,a2=bond.a1,bond.a2
            poly=Cylinder(center=(a1.coord+a2.coord)/2,direction=a2.coord-a1.coord,radius=0.1)
            self.plotter.add_mesh(poly,name=bond.idx,pickable=False,pbr=True,metallic=0.5)
    
    def add_labels(self):
        """添加原子的label"""
        points=self.mol.coords
        labels=[f'{i}' for i in range(len(points))]
        self.plotter.add_point_labels(points,labels,always_visible=True)

    def hide_cloud(self,names):
        """
        将非指定点云全部隐藏，并返回指定的点云是否已经存在
        """
        render=self.plotter.renderer
        actors=render.actors
        exist=False
        for key in actors:
            if key.split('-')[0]=='cloud':
                if key in names:
                    actors[key].visibility=True
                    exist=True
                else:
                    actors[key].visibility=False

        return exist

    def show_cloud(self,obt:int):
        """
        显示指定原子的轨道
        """
        if len(self.selectedAtoms)==0:
            print('尚未选择原子')
            return
        self.app.showMessage('正在计算...')
        # 根据原子计算点云应该存在的位置
        print(self.selectedAtoms)
        atoms=[int(a.split('-')[1])-1 for a in self.selectedAtoms]
        atoms.sort()
        atomStr=','.join([str(a) for a in atoms])
        name=f'{atomStr}-{obt}'
        exist=self.hide_cloud([f'cloud-N-{name}',f'cloud-P-{name}'])
        if exist:return # 如果已经存在的话就没必要再添加了
        
        coords=self.mol.coords[atoms,:]
        minX,minY,minZ=np.min(coords,axis=0)
        maxX,maxY,maxZ=np.max(coords,axis=0)
        step=0.1

        Rx=np.arange(minX-self.borderValue,maxX+self.borderValue+0.1,step)
        Ry=np.arange(minY-self.borderValue,maxY+self.borderValue+0.1,step)
        Rz=np.arange(minZ-self.borderValue,maxZ+self.borderValue+0.1,step)
        origin=np.array([Rx[0],Ry[0],Rz[0]])
        Lx,Ly,Lz=len(Rx),len(Ry),len(Rz) #每个轴的长度
        X,Y,Z=np.meshgrid(Rx,Ry,Rz)
        pos=np.array([X.flatten(),Y.flatten(),Z.flatten()]).T

        values=np.zeros(len(pos))
        # print(values.shape,pos.shape)
        for i in atoms:
            atom=self.mol.atoms[i]
            values+=atom.get_cloud(pos-atom.coord,obt)
        # P:positive，N:negative
        values=values.reshape(Lx,Ly,Lz) # 转成三位数组
        # self.add_cloud_surface(values,origin,(0.2,1),name='P')
        # self.add_cloud_surface(values,origin,(-1,-0.2),name='N')
        
        valuesUnits = np.divide(values, np.abs(values), out=np.zeros_like(values), where=values!=0)
        values=np.where((values>self.isoValue) | (values<-self.isoValue),1.,0.)
        values[[0,-1],:,:]=0
        values[:,[0,-1],:]=0
        values[:,:,[0,-1]]=0

        valuesX0=np.zeros_like(values)
        valuesX1=np.zeros_like(values)
        valuesY0=np.zeros_like(values)
        valuesY1=np.zeros_like(values)
        valuesZ0=np.zeros_like(values)
        valuesZ1=np.zeros_like(values)

        valuesX0[1:,:,:]=values[:-1,:,:]
        valuesX1[:-1,:,:]=values[1:,:,:]

        valuesY0[:,1:,:]=values[:,:-1,:]
        valuesY1[:,:-1,:]=values[:,1:,:]

        valuesZ0[:,:,1:]=values[:,:,:-1]
        valuesZ1[:,:,:-1]=values[:,:,1:]

        valuesR=values+valuesX0+valuesX1+valuesY0+valuesY1+valuesZ0+valuesZ1 #原来的点与周围方向的点的加和

        valuesR=np.where((valuesR==0)|(valuesR==7),0.,1.) #满足条件的为1，不满足条件的为0
        valuesR*=valuesUnits #为所有值赋予单位，正1或负1
        valuesR=valuesR.flatten() #拉平

        idxsP=np.argwhere(valuesR>0).flatten()
        idxsN=np.argwhere(valuesR<0).flatten()
        posP=pos.copy()[idxsP]
        posN=pos.copy()[idxsN]
        self.add_cloud(posP,'red',f'cloud-P-{name}')
        self.add_cloud(posN,'blue',f'cloud-N-{name}')
        self.app.showMessage('计算完成')

    def add_cloud_surface(self,values:np.ndarray,origin:np.ndarray,value,name):
        grid = pv.UniformGrid()
        grid.dimensions = np.array(values.shape) + 1
        grid.spacing = (0.1, 0.1, 0.1)
        grid.origin = origin
        
        grid.cell_data["values"] = values.flatten(order="F")
        vol = grid.threshold(value=value)
        print(vol.number_of_cells)
        if vol.number_of_cells==0:
            return
        surf = vol.extract_geometry()
        smooth = surf.smooth(n_iter=500)
        self.plotter.add_mesh(smooth,color='pink',opacity=0.5,smooth_shading=True,name=name)

    def add_cloud(self,points,color:str,name:str):
        if len(points)>0:
            cloud=pv.PolyData(points)
            self.plotter.add_mesh(cloud,color=color,opacity=0.5,
                reset_camera=False,name=name,pickable=False)
        else:
            print('没有点')

    def onClick(self,mesh:PolyData): #使选中的原子改变颜色
        if not hasattr(mesh,'name'):return
        name:str=mesh.name
        symbol,idx=name.split('-')
        actor=self.get_actor(name)
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
    
    def get_actor(self,name)->Actor:
        """
        根据name获取actor
        """
        actors:dict=self.plotter.renderer.actors
        names=actors.keys()
        if name in names:
            return actors[name]
        else:
            return None


    def get_atom(self,idx:int)->Actor:
        """
        根据原子标签获取原子对象
        """
        atom=self.mol.atom(idx)
        name=f'{atom.symbol}-{idx}'
        return self.get_actor(name)


    def set_color(self,idx:int,color=None):
        """
        设置原子的颜色，如果不传入任何参数则使用原子默认颜色
        """
        symbol=self.mol.atom(idx).symbol
        if color is None:color=elements[symbol].color
        self.get_atom(idx).prop.SetColor(utils.hex2rgb(color))
    
    def reset_color(self):
        """将所有的原子回复原本的颜色"""
        idxs=[a.idx for a in self.mol.atoms]
        for idx in idxs:
            self.set_color(idx)


    def set_colors(self,idxs:List[int],values:List[float]):
        """
        根据数值计算对应的颜色并修改
        idxs:原子指标
        values:原子对应的数值
        idx与values的长度应该相等
        """
        values:np.ndarray=np.array(values)
        ratios=(values-values.min())/(values.max()-values.min()) #将数值映射到0-1之间
        # 将数值映射到颜色值为两个值之间
        for idx,ratio in zip(idxs,ratios):
            color=color_bar(ratio)
            self.set_color(idx,color)

    def add_arrow(self,center,direction,ratio):
        """向场景中添加箭头"""
        color=color_bar(ratio)
        self.plotter.add_arrows(center,direction,color=color,mag=1+ratio/2)
    
    def add_arrows_(self,idxs,values):
        values:np.ndarray=np.array(values)
        ratios=(values-values.min())/(values.max()-values.min()) #将数值映射到0-1之间
        # 将数值映射到颜色值为两个值之间
        for idx,ratio in zip(idxs,ratios):
            atom=self.mol.atom(idx)
            center=atom.coord
            direction=atom.get_Normal()
            self.add_arrow(center,direction,ratio)

        


def color_bar(ratio:float):
    c0=np.array([0.,0.,1.])
    c1=np.array([1.,0.,0.])
    color:np.ndarray=(c0+(c1-c0)*ratio)*255
    r,g,b=color.astype(int)
    hexColor=f'#{r:0>2x}{g:0>2x}{b:0>2x}'
    return hexColor
