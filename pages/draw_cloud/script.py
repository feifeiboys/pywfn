import numpy as np
from ..utils import posan_function,get_coefficients,get_gridPoints
class Render:
    def __init__(self,program) -> None:
        self.program=program
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
                    ts=self.atoms[atom]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,orbital] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
                    aroundPos=centerPos+self.arounds
                    values=posan_function(centerPos=centerPos,aroundPos=aroundPos,alphas=paras[:,0],cs=paras[:,2],ts=ts)
                    print(aroundPos.shape,values.shape)
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
                    center_ts=get_coefficients('P',self.Data.atoms,center,orbital,raw=True)
                    around_paras = np.array(self.Data.standard_basis[around])
                    around_ts=get_coefficients('P',self.Data.atoms,around,orbital,raw=True)
                    bondGrid=(centerPos+aroundPos)/2+self.gridPointsBox
                    centerArray=posan_function(centerPos,bondGrid,center_paras[:,0],center_paras[:,2],center_ts)
                    aroundArray=posan_function(aroundPos,bondGrid,around_paras[:,0],around_paras[:,2],around_ts)
                    self.saveArray(f'{self.program.dataForder}//{center+1}-{around+1}-{orbital+1}',np.concatenate([bondGrid,centerArray+aroundArray]).T)
    def saveArray(self,file,array):
        if file not in self.savedArray:
            np.save(file=file,arr=array)
