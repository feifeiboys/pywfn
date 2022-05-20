import numpy as np
from ..utils import posan_function,get_coefficients,get_gridPoints
class Render:
    def __init__(self,program) -> None:
        self.program=program
        self.orbital_type=self.program.Data.orbital_type
        self.Data=program.Data
        size=program.config['renderSize']
        step=program.config['renderStep']
        xs=[]
        ys=[]
        zs=[]
        for x in np.arange(-size,size,step):
            for y in np.arange(-size,size,step):
                for z in np.arange(-size,size,step):
                    xs.append(x)
                    ys.append(y)
                    zs.append(z)
        self.arounds=np.array([xs,ys,zs])
        self.set_data()
        self.gridPointsBox=get_gridPoints(2,0.1,ball=True)
        self.savedArray=[]


    def set_data(self):
        Data=self.program.Data
        for each in dir(Data):
            if each[0]!='_':
                setattr(self,each,getattr(Data,each))

    def get_atomPos(self,atom):  # 获取指定原子的坐标
        x = self.atoms_pos.iloc[atom].loc['X'] # 中心原子坐标
        y = self.atoms_pos.iloc[atom].loc['Y']
        z = self.atoms_pos.iloc[atom].loc['Z']
        return np.array([x,y,z])


    def atomRender(self,atoms,orbitals):
        cloudData={}
        for atom in atoms:
            if self.atoms[atom]['atom_type']!='H':
                for orbital in orbitals:
                    centerPos=self.get_atomPos(atom).reshape(3,1)
                    paras = np.array(self.standard_basis[atom])
                    # ts=self.atoms[atom]['datas'].loc[['2S','2PX','2PY','2PZ','3S','3PX','3PY','3PZ'],:].iloc[:,orbital] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
                    ts=get_coefficients('2SP',self.Data.atoms,atom,orbital,raw=True)
                    # aroundPos=centerPos+self.arounds
                    atomGrid=centerPos+self.gridPointsBox
                    values=posan_function(centerPos=centerPos,aroundPos=atomGrid,paras=paras,ts=ts)
                    if self.orbital_type==0:
                        self.saveArray(f'{self.program.dataForder}//atomClouds//{atom+1}-{orbital+1}',np.concatenate([atomGrid,values]).T)
                    elif self.orbital_type==1:
                        orbital_name=f'a,{orbital+1}'
                        if orbital>self.program.Data.orbital_length/2-1:
                            orbital_name=f'b,{int(orbital-self.program.Data.orbital_length/2+1)}'
                        self.saveArray(f'{self.program.dataForder}//atomClouds//{atom+1}-{orbital_name}',np.concatenate([atomGrid,values]).T)
                    cloudData[f'{atom}-{orbital}']=values.tolist()
        self.program.server.setCloud(cloudData)
        self.program.log_window_text.insert('end','rendering complete, view in browser\n')
    def bondRender(self,atoms,orbitals):
        for center in atoms:
            connections=self.Data.connections(center).copy()
            for around in connections:
                if self.Data.atoms[around]['atom_type']=='H':
                    continue
                for orbital in orbitals:
                    centerPos=self.Data.atomPos(center).reshape(3,1)
                    aroundPos=self.Data.atomPos(around).reshape(3,1)
                    center_paras = np.array(self.Data.standard_basis[center])
                    center_ts=get_coefficients('2SP',self.Data.atoms,center,orbital,raw=True)
                    around_paras = np.array(self.Data.standard_basis[around])
                    around_ts=get_coefficients('2SP',self.Data.atoms,around,orbital,raw=True)
                    bondGrid=(centerPos+aroundPos)/2+self.gridPointsBox
                    centerArray=posan_function(centerPos,bondGrid,center_paras,center_ts)
                    aroundArray=posan_function(aroundPos,bondGrid,around_paras,around_ts)
                    if self.orbital_type==0:
                        self.saveArray(f'{self.program.dataForder}//bondClouds//{center+1}-{around+1}-{orbital+1}',np.concatenate([bondGrid,centerArray+aroundArray]).T)
                    elif self.orbital_type==1:
                        orbital_name=f'a,{orbital+1}'
                        if orbital>self.program.Data.orbital_length/2-1:
                            orbital_name=f'b,{int(orbital-self.program.Data.orbital_length/2+1)}'
                        print(orbital_name)
                        self.saveArray(f'{self.program.dataForder}//bondClouds//{center+1}-{around+1}-{orbital_name}',np.concatenate([bondGrid,centerArray+aroundArray]).T)
    def saveArray(self,file,array):
        if file not in self.savedArray:
            np.save(file=file,arr=array)
