import numpy as np
from ..utils import posan_function
class Render:
    def __init__(self,program) -> None:
        self.program=program
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


    def render(self,atoms,orbitals):
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
