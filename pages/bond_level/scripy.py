import numpy as np
import pandas as pd
import math
import sympy
import matplotlib.pyplot as plt
import sys

class Caculater:
    def __init__(self, program):
        self.program = program
        self.logger=program.logger
        self.normals={} # 计算每个原子的法向量
        self.point2={} # 计算每个原子上下两点处函数值
        self.searched=[] #记录已经搜索的原子
        self.obtial_type = None # 轨道类型，是否为劈裂
        self.atoms_pos = None
        self.atoms = None
        self.standard_basis = None
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
        # self.get_allNormals()

    def get_atomPos(self,atom):  # 获取指定原子的坐标
        x = self.atoms_pos.iloc[atom].loc['X'] # 中心原子坐标
        y = self.atoms_pos.iloc[atom].loc['Y']
        z = self.atoms_pos.iloc[atom].loc['Z']
        return np.array([x,y,z])

    def get_functionValue(self,center,aroundPos,obtial): #获得中心原子周围某一点（这一点不确定所以要自己指定）处的函数值
        centerPos=self.get_atomPos(center) #中心原子坐标
        paras = np.array(self.standard_basis[center])
        ts=self.atoms[center]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
        res=self.function(centerPos,aroundPos,paras[:,0],paras[:,2],ts)
        return res

    def function(self,centerPos,aroundPos,alphas,cs,ts): # 为了代码可读性，可以适当写出来罗嗦点的代码
        x,y,z=aroundPos
        x0,y0,z0=centerPos
        R=np.sum((centerPos-aroundPos)**2)
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

    def get_cloud(self,center, connect, obtial):  # 获取中心原子和周围原子之间十个点的函数值
        results=[]
        centerPos=self.get_atomPos(center) #中心原子坐标
        connectPos=self.get_atomPos(connect) #相连原子坐标
        all_aroundPos=[centerPos+(connectPos-centerPos)*(i/9) for i in range(10)]
        self.logger.info(f'{center+1}->{connect+1}:10 pos={all_aroundPos}')
        ts=self.atoms[center]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
        tsu=ts.copy()
        tsu=np.where(tsu>0,1,tsu)
        tsu=np.where(tsu<0,-1,tsu)
        ts=(ts**2/self.all_sauare_sum[obtial])**0.5*tsu #将ts归一化
        for aroundPos in all_aroundPos:
            res=self.get_functionValue(center,aroundPos,obtial)
            results.append(res)
        return np.array(results)
    
    def get_normalVector(self,p1,p2,p3):
        A,B,C,D=sympy.symbols('A,B,C,D')
        x1,y1,z1=p1
        x2,y2,z2=p2
        x3,y3,z3=p3
        res=sympy.solve([
            A*x1+B*y1+C*z1+D,
            A*x2+B*y2+C*z2+D,
            A*x3+B*y3+C*z3+D,
        ],[A,B,C,D])
        keys=list(res.keys())
        if A not in keys:
            n=np.array([1,0,0])
        elif B not in keys:
            n=np.array([0,1,0])
        elif C not in keys:
            n=np.array([0,0,1])
        elif D not in keys:
            n=np.array([float(res[each].subs(D,1)) for each in [A,B,C]])
            n=n/(np.sum(n**2))**0.5
        return n*0.2
    def get_Normal(self,atom): #对获得标量函数的封装
        if f'{atom}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            atomPos=self.get_atomPos(atom)
            connections=self.get_connections(atom)
            p1,p2,p3=[self.get_atomPos(each)-atomPos for each in connections]
            n=self.get_normalVector(p1,p2,p3)
            self.normals[f'{atom}']=n
            print(atom,n)
        return self.normals[f'{atom}']
    def set_Normal(self,atom,norm):
        self.normals[f'{atom}']=norm
    def search_Normal(self,atom): #递归搜索向量(要十分小心，不然程序就死了),i为搜索次数,s为已经搜索的原子
        connections=self.get_connections(atom) # 该原子连接的原子
        # 下一轮搜索就不要搜索已经搜过的了
        print(connections,len(connections))
        if len(connections)==3:
            n=self.get_Normal(atom)
            return n
        if len(connections)==4 or len(connections)==2 or len(connections)==1:
            for each in connections:
                if len(self.get_connections(each))==3:
                    return self.get_Normal(each)
            self.searched.append(atom)
            for each in connections:
                if self.atoms[each]['atom_type']=='H':
                    continue
                if each not in self.searched:
                    print('递归搜索',atom+1,len(connections),[each+1 for each in connections],each)
                    return self.search_Normal(each)
                
        else:
            print(f'{atom},连接数量错误,{len(connections)}')
    # 判断两个原子之间的轨道是不是π轨道,(中心原子序号，周围原子序号，轨道序号)
    def get_allNormals(self): #直接尝试获取所有原子法向量
        self.program.log_window_text.insert('end','正在计算所有原子法向量...')
        for atom in range(len(self.atoms)):
            if self.atoms[atom]['atom_type']!='H':
                print('开始搜索法向量',atom+1)
                n=self.search_Normal(atom)
                self.set_Normal(atom,n)
                self.searched.clear()
            else:
                self.set_Normal(atom,None) #H原子也没有法向量
            self.program.update_progress('获取原子法向量',(atom+1)/len(self.atoms))
        self.program.server.set_normals(self.normals)
        
    def get_obtial_is_userful(self, center, around, obtial):  # 这里传入的应当是用户输入的
        all_square_sum = self.all_sauare_sum[obtial]
        centerPs=self.atoms[center]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial]
        p_sums_center=np.sum(centerPs**2/all_square_sum)
        aroundPs=self.atoms[around]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial]
        p_sums_around = np.sum(aroundPs**2/all_square_sum)
        # 针对通用体系想出来的方法
        self.logger.info(f'*'*70)
        self.logger.info(f'center:{center+1},around:{around+1},obtial:{obtial+1}')
        self.logger.info(f'cpSum:{p_sums_center},apSum:{p_sums_around}')
        if max([p_sums_center,p_sums_around]) <= self.program.config['judgeValues'][0]:
            self.logger.info('1 step pass')
            return False
        
        centerPos=self.get_atomPos(center)
        aroundPos=self.get_atomPos(around)
        # 计算两原子键轴中间处的函数值，如果太大则不是π轨道
        pos=(centerPos+aroundPos)/2
        value=abs(self.get_functionValue(center,pos,obtial)+self.get_functionValue(around,pos,obtial))/2
        if value>0.1:
            self.logger.info(f'bondValue:{value}')
            return False
        

        # 求出过与中心原子相连的三个原子的平面的法向量
        cn=self.normals[f'{center}']
        an=self.normals[f'{around}']
        cv1=self.get_functionValue(center,centerPos+cn,obtial) #不同情况只是法向量不同，但是原子的位置归根到底是不会变的，所以确定法向量即可确定四处函数值
        cv2=self.get_functionValue(center,centerPos-cn,obtial)
        av1=self.get_functionValue(around,aroundPos+an,obtial)
        av2=self.get_functionValue(around,aroundPos-an,obtial)
        self.point2[f'{around}-{obtial}']=[av1,av2] #保存每两个分子的法向量值
        self.point2[f'{center}-{obtial}']=[cv1,cv2]
        value=np.min(np.abs(np.array([cv1,cv2,av1,av2])))
        self.logger.info(f'cv1={cv1},cv2={cv2},av1={av1},av2={av2},value={value}')
        if  cv1*cv2<0 and av1*av2<0 and value>0.024: #根据这四个数值也能判断原子之间轨道贡献正负
            return True
        else:
            return False

    def obtial_between_atoms(self, center, around):  # 挑选两个原子之间π键有哪些
        userful = []
        obtial_num = self.obtial_length

        for obtial in range(obtial_num):  # 所有的O轨道都判断
            # 如果当前轨道不是占据轨道则直接跳过
            if self.obtials[obtial][-1]!='O':
                continue
            if self.obtial_type == 0:
                res = self.get_obtial_is_userful(center, around,obtial)
                if res:
                    userful.append(obtial)
            if self.obtial_type == 1:
                res = self.get_obtial_is_userful(center,around,obtial)
                if res:
                    userful.append(obtial)
        return userful

    def get_connections(self, atom):  # 计算所有原子与指定原子之间的距离,进而判断与之相连的原子
        atoms_pos = self.atoms_pos
        dxs = atoms_pos.loc[:, 'X'] - atoms_pos.iloc[atom].loc['X']
        dys = atoms_pos.loc[:, 'Y'] - atoms_pos.iloc[atom].loc['Y']
        dzs = atoms_pos.loc[:, 'Z'] - atoms_pos.iloc[atom].loc['Z']
        distances = (dxs ** 2 + dys ** 2 + dzs ** 2) ** 0.5
        res = np.where(distances < 1.7)[0].tolist()
        res.remove(atom)
        return res

    def get_unit(self, center, around, obtial):  # 判断两原子之间的正负关系
        # 计算两个原子间法向量的夹角
        n1=self.normals[f'{center}']
        n2=self.normals[f'{around}']
        angle=np.arccos(np.dot(n1,n2)/(np.sqrt(np.dot(n1,n1))*np.sqrt(np.dot(n2,n2))))/np.pi
        res=np.sum(np.array(self.point2[f'{center}-{obtial}']*np.array(self.point2[f'{around}-{obtial}'])))
        if angle>0.5:
            res*=-1
        self.logger.info(f'{center+1},{around+1},{obtial+1},res={res},angle={angle}')
        return 1 if res > 0 else -1

    def get_bond_level_between_tow_atom(self, center, around):  # 计算两个原子之间的键级
        userful_obtials = self.obtial_between_atoms(center,around) # 挑选π键级
        around_units = [self.get_unit(center, around, obtial) for obtial in userful_obtials] # 周围原子与中心原子之间的正负系数
        around_units = np.array(around_units).reshape(1, len(userful_obtials))
        center_units = np.ones((1, len(userful_obtials)))

        if self.obtial_type == 0:
            userful_str = [str(i+1) for i in userful_obtials]
            self.program.log_window_text.insert('end',f'{center+1}->{around+1}π轨道：'+','.join(userful_str)+'\n')
        else:
            userful_str = [f'α{i+1}' if i < self.alpha_num else f'β{i+1-self.alpha_num}' for i in userful_obtials]
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},π轨道：' + ','.join(userful_str) + '\n')
        all_square_sum = self.all_sauare_sum[np.newaxis, :][:, userful_obtials]
        center_square_sum = self.each_square_sum[center, userful_obtials]
        around_square_sum = self.each_square_sum[around, userful_obtials]
        center_res = (center_square_sum / all_square_sum) ** 0.5 * center_units
        around_res = (around_square_sum / all_square_sum) ** 0.5 * around_units
        bond_level = np.sum((2 if self.obtial_type == 0 else 1) * center_res * around_res)
        return bond_level

    def get_atom_bond_levels(self, center, arounds):  # 计算某个原子与周围原子之间的键级
        bond_levels = []
        cn=self.search_Normal(center) #中心原子法向量
        self.set_Normal(center,cn)
        for around in arounds:
            if self.atoms[around]['atom_type']=='H':
                self.set_Normal(around,None) #H原子也没有法向量
                continue
            an=self.search_Normal(around)
            # an=cn
            self.set_Normal(around,an)
            if self.normals[f'{center}'] is not None and self.normals[f'{around}'] is not None:
                bond_level = self.get_bond_level_between_tow_atom(center, around)
            else:
                bond_level=0
            bond_levels.append(bond_level)
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},键级:{bond_level}\n')
        self.program.server.set_normals(self.normals)
        return np.array(bond_levels)
    