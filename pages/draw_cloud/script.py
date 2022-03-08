import numpy as np
import math
import pandas as pd

class Render:
    def __init__(self,program) -> None:
        self.program=program
        space=np.arange(-1,1,0.1)
        self.arounds=np.array([each.flatten() for each in np.meshgrid(space,space,space)])
        self.set_data()


    def set_data(self):
        data=self.program.data
        keys = data.keys()
        if 'Standard orientation' in keys:
            self.atoms_pos = data['Standard orientation']
        # 轨道类型有两种情况，正常的和劈裂为α、β的
        if 'Molecular Orbital Coefficients' in keys:
            self.obtial_type = 0
            self.atoms = data['Molecular Orbital Coefficients'] # [O,O,O,V,V,V]
            obtial_num = data['Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{obtial_num}个轨道\n')
        elif ('Alpha Molecular Orbital Coefficients' in keys) and ('Beta Molecular Orbital Coefficients' in keys):
            self.alpha_num = data['Alpha Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.beta_num = data['Beta Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{self.alpha_num}个Alpha轨道和{self.beta_num}个Beta轨道\n')
            self.obtial_type = 1
            self.atoms = [{
                'atom_id': alpha['atom_id'],
                'atom_type': alpha['atom_type'],
                'datas': pd.concat([alpha['datas'], beta['datas']], axis=1), # 将α和β的轨道数据横向拼接在一起[O,O,O,V,V,V,O,O,O,V,V,V]
                'obtials': alpha['obtials'] + beta['obtials']
            } for alpha, beta in
                zip(data['Alpha Molecular Orbital Coefficients'], data['Beta Molecular Orbital Coefficients'])]
        self.obtials=self.atoms[0]['datas'].columns # 所有的轨道类型(占据或非占据，可能会有复杂的表示)
        print(self.obtials)
        self.obtial_length = self.atoms[0]['datas'].shape[1] # 轨道的数量
        if 'Standard basis' in data.keys():
            self.standard_basis = data['Standard basis']
        self.each_square_sum=np.concatenate([np.sum(atom['datas'].to_numpy()**2,axis=0,keepdims=True) for atom in self.atoms])
        print(self.each_square_sum.shape)
        self.all_sauare_sum=self.each_square_sum.sum(axis=0) # 所有原子所有轨道的平方和

    def get_atomPos(self,atom):  # 获取指定原子的坐标
        x = self.atoms_pos.iloc[atom].loc['X'] # 中心原子坐标
        y = self.atoms_pos.iloc[atom].loc['Y']
        z = self.atoms_pos.iloc[atom].loc['Z']
        return np.array([x,y,z])

    def function(self,centerPos,alphas,cs,ts): # 为了代码可读性，可以适当写出来罗嗦点的代码
        aroundPos=centerPos+self.arounds
        x,y,z=aroundPos
        x0,y0,z0=centerPos
        R=np.sum((centerPos-aroundPos)**2,axis=0,keepdims=True)
        def psx(a):
            return (2*a/math.pi)**(3/4)*2*a**0.5*(x-x0)*math.e**(-1*a*R)
        def psy(a):
            return (2*a/math.pi)**(3/4)*2*a**0.5*(y-y0)*math.e**(-1*a*R)
        def psz(a):
            return (2*a/math.pi)**(3/4)*2*a**0.5*(z-z0)*math.e**(-1*a*R)
        px2=sum([c*psx(a) for c,a in zip(cs[:-1],alphas[:-1])])  # 对于3-21
        py2=sum([c*psy(a) for c,a in zip(cs[:-1],alphas[:-1])])
        pz2=sum([c*psz(a) for c,a in zip(cs[:-1],alphas[:-1])])
        px3=cs[-1]*psx(alphas[-1])
        py3=cs[-1]*psy(alphas[-1])
        pz3=cs[-1]*psz(alphas[-1])
        ps=[px2,py2,pz2,px3,py3,pz3]
        mo=sum([t*p for t,p in zip(ts,ps)])
        return mo

    def render(self,atoms,obtials):
        cloudData={}
        for atom in atoms:
            if self.atoms[atom]['atom_type']!='H':
                for obtial in obtials:
                    centerPos=self.get_atomPos(atom).reshape(3,1)
                    paras = np.array(self.standard_basis[atom])
                    ts=self.atoms[atom]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
                    x,y,z=aroundPos=centerPos+self.arounds
                    values=self.function(centerPos=centerPos,alphas=paras[:,0],cs=paras[:,2],ts=ts)
                    print(x.shape,y.shape,z.shape,values.shape)
                    cloudData[f'{atom}-{obtial}']=values.tolist()
        self.program.server.setCloud(cloudData)
