##该脚本用来展示分子3D模型
import threading
import pyvista as pv
import numpy as np
import json
class Viewer:
    def __init__(self,Data,server) -> None:
        with open('materials.json','r',encoding='utf-8') as f:
            self.materials=json.loads(f.read())
        self.server=server
        self.plotter=pv.Plotter()
        self.plotter.add_axes()
        self.Data=Data
        atom_pos=Data.atoms_pos.loc[:,['X','Y','Z']].to_numpy()
        for index,pos in enumerate(atom_pos):
            self.add_atom(pos,index)
        for i,pos_i in enumerate(atom_pos):
            for j,pos_j in enumerate(atom_pos[i:,:]):
                distance=np.linalg.norm((pos_i-pos_j))
                if distance<1.7:
                    self.add_bond((pos_i+pos_j)/2,(pos_i-pos_j),distance)


    def add_atom(self,pos,index):
        atomType=self.Data.atoms[index]['atom_type']
        material=self.materials[atomType]
        sphere=pv.Sphere(center=pos,theta_resolution=30,phi_resolution=30,radius=material['radius'])
        self.plotter.add_mesh(sphere,smooth_shading=True,pbr=True,color=material['color'][:-1],roughness=material['roughness'],opacity=material['color'][-1])

    def add_bond(self,position,direction,length):
        bond=pv.Cylinder(center=position, direction=direction,radius=0.1, height=length)
        self.plotter.add_mesh(bond)

    def add_vector(self,start,direction):
        arrow=pv.Arrow(start=start,direction=direction)
        self.plotter.add_mesh(arrow,color='yellow')

    def show(self):
        t=threading.Thread(target=lambda:self.plotter.show())
        t.start()
        