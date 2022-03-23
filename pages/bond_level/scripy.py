import numpy as np
import math
from pages.utils import get_vertical,posan_function,get_gridPoints,vector_angle,get_normalVector,obtial_classify

class Caculater:
    def __init__(self, program):
        self.program = program
        self.logger=program.logger
        self.normals={} # 计算每个原子的法向量
        self.pvectors={}
        self.point2={} # 计算每个原子上下两点处函数值
        self.searched=[] #记录已经搜索的原子
        self.set_data()
        self.gridPoints=get_gridPoints(1,0.2)
        

    def set_data(self):
        Data=self.program.Data
        for each in dir(Data): #将Data对象的自定义属性赋值到self
            if each[0]!='_':
                setattr(self,each,getattr(Data,each))
        
    def get_atomPos(self,atom):  # 获取指定原子的坐标
        x = self.atoms_pos.iloc[atom].loc['X'] # 中心原子坐标
        y = self.atoms_pos.iloc[atom].loc['Y']
        z = self.atoms_pos.iloc[atom].loc['Z']
        return np.array([x,y,z])


    def get_Normal(self,atom): #对获得标量函数的封装
        if f'{atom}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            atomPos=self.get_atomPos(atom)
            connections=self.get_connections(atom)
            p1,p2,p3=[self.get_atomPos(each)-atomPos for each in connections]
            n=get_normalVector(p1,p2,p3)
            self.normals[f'{atom}']=n
        return self.normals[f'{atom}']
    def set_Normal(self,atom,norm):
        self.normals[f'{atom}']=norm
    def search_Normal(self,atom): #递归搜索向量(要十分小心，不然程序就死了)
        connections=self.get_connections(atom) # 该原子连接的原子
        # 下一轮搜索就不要搜索已经搜过的了
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
                    # print('递归搜索',atom+1,len(connections),[each+1 for each in connections],each)
                    return self.search_Normal(each)
        else:
            print(f'{atom},连接数量错误,{len(connections)}')
    # 判断两个原子之间的轨道是不是π轨道,(中心原子序号，周围原子序号，轨道序号)
    
    def get_obtial_is_userful(self, center, around, obtial):  # 这里传入的应当是用户输入的
        if self.atoms[around]['atom_type']=='H':
            return False
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
            return False # 判断条件1，s轨道的数值太小的排除
        
        centerPos=self.get_atomPos(center).reshape(3,1)
        aroundPos=self.get_atomPos(around).reshape(3,1)
        # 计算两原子键轴中间处的函数值，如果太大则不是π轨道
        # 去键轴上十个点，分别带入函数求得函数值
        center_paras = np.array(self.standard_basis[center])
        center_ts=self.atoms[center]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
        around_paras = np.array(self.standard_basis[around])
        around_ts=self.atoms[around]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtial] #获取某个原子某个轨道的2px,2py,2pz,3px,3py,3pz
        if self.N==3:
            # 求出过与中心原子相连的三个原子的平面的法向量
            cn=self.normals[f'{center}']
            an=self.normals[f'{around}']
            cns=cn.reshape(3,1)*np.arange(0.1,3.0,0.1)[np.newaxis,:]
            ans=an.reshape(3,1)*np.arange(0.1,3.0,0.1)[np.newaxis,:]
            cv1s=posan_function(centerPos,centerPos+cns,center_paras[:,0],center_paras[:,2],center_ts)
            cv2s=-cv1s
            av1s=posan_function(aroundPos,aroundPos+ans,around_paras[:,0],around_paras[:,2],around_ts)
            av2s=-av1s
            if np.max(cv1s)*np.min(cv1s)<=0 or np.max(av1s)*np.min(av1s)<=0:  # 法向量方向上不能有节点
                return False
            vc=get_vertical(cn,(aroundPos-centerPos).flatten()).reshape(3,1) #垂直于键轴和法向量的单位向量 
            vcv=posan_function(centerPos,centerPos+vc*0.2,center_paras[:,0],center_paras[:,2],center_ts)
            cv1=cv1s[0][1] #不同情况只是法向量不同，但是原子的位置归根到底是不会变的，所以确定法向量即可确定四处函数值
            self.logger.info(f'vc:{vc},vcv:{vcv},cv1:{cv1},differ:{abs(cv1)-abs(vcv)}')
            if abs(cv1)-abs(vcv)<0: # 法向量方向的函数值要大于垂直于法向量和键轴方向的函数值
                return False
            cv2=cv2s[0][1]
            av1=av1s[0][1]
            av2=av2s[0][1]
            self.point2[f'{around}-{obtial}']=[av1,av2] #保存每两个分子的法向量值
            self.point2[f'{center}-{obtial}']=[cv1,cv2]
            value=np.min(np.abs(np.array([cv1,cv2,av1,av2])))
            self.logger.info(f'cv1={cv1},cv2={cv2},av1={av1},av2={av2},value={value}')
            if  cv1*cv2<0 and av1*av2<0 and value>0.03: #根据这四个数值也能判断原子之间轨道贡献正负，法向量与法向量反方向不能同号
                return True
            else:
                return False
        if self.N==2:
            cvs=posan_function(centerPos,centerPos+self.gridPoints,center_paras[:,0],center_paras[:,2],center_ts)
            avs=posan_function(aroundPos,aroundPos+self.gridPoints,around_paras[:,0],around_paras[:,2],around_ts)
            c_maxID=np.argmax(cvs)
            a_maxID=np.argmax(avs)
            c_pv=self.gridPoints[:,c_maxID]
            a_pv=self.gridPoints[:,a_maxID]
            b_vector=aroundPos-centerPos

            c_angle=vector_angle(c_pv,b_vector)
            a_angle=vector_angle(a_pv,b_vector)
            c_value,a_value=np.max(cvs),np.max(avs)

            self.logger.info(f'c_value{c_value},a_value{a_value}')
            self.logger.info(f'c_angle{c_angle},a_angle{a_angle}')
            self.pvectors[f'{center}-{obtial}']=c_pv  #只有连接数是2的时候法向量为
            self.pvectors[f'{around}-{obtial}']=a_pv
            self.point2[f'{center}-{obtial}']=[c_value,-c_value]
            self.point2[f'{around}-{obtial}']=[a_value,-a_value] #保存每两个分子的法向量值
            if min([abs(c_angle-0.5),abs(a_angle-0.5)])<0.1 and min([c_value,a_value])>0.04:
                
                return True
            else:
                return False
        else:
            return False

    def get_obtial_between_atoms(self, center, around):  # 挑选两个原子之间π键有哪些
        obtial_num = self.obtial_length
        O_obtials=[]
        V_obtials=[]
        for obtial in range(obtial_num):  # 所有的O轨道都判断
            # 如果当前轨道不是占据轨道则直接跳过
            obtialName=self.obtials[obtial]
            res = self.get_obtial_is_userful(center,around,obtial)
            if obtialName[-1]=='O':
                if res:
                    O_obtials.append(obtial)
            elif obtialName[-1]=='V':
                
                if res:
                    V_obtials.append(obtial)
            else:
                print(f'unkonw:{obtialName},{obtialName[-1]}')
        return O_obtials,V_obtials

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
        if self.N==3:
            n1=self.normals[f'{center}']
            n2=self.normals[f'{around}']
            angle=vector_angle(n1,n2)
            res=np.sum(np.array(self.point2[f'{center}-{obtial}']*np.array(self.point2[f'{around}-{obtial}'])))
            if angle>0.5:
                res*=-1
            self.logger.info(f'{center+1},{around+1},{obtial+1},res={res},angle={angle}')
            return 1 if res > 0 else -1
        if self.N==2:
            n1=self.pvectors[f'{center}-{obtial}']
            n2=self.pvectors[f'{around}-{obtial}']
            angle=vector_angle(n1,n2)
            return 1 if angle<=0.5 else -1

    def get_bond_level_between_tow_atom(self, center, around):  # 计算两个原子之间两个方向的键级（平面分子只有一个，线性分子有两个，分别用V和H表示）
        O_obtials,V_obtials=self.get_obtial_between_atoms(center,around)
        bond_orders=[]
        if self.N==3:
            way_obtials=[O_obtials,[]]
        if self.N==2:
            Vo,Ho=obtial_classify(center,self.pvectors,O_obtials)
            self.logger.info(f'{Vo=}\n{Ho=}')
            way_obtials=[Vo,Ho]
        for i,way_obtial in enumerate(way_obtials):
            around_units = [self.get_unit(center, around, obtial) for obtial in way_obtial] # 周围原子与中心原子之间的正负系数
            self.logger.info(f'units:{around_units}')
            around_units = np.array(around_units).reshape(1, len(way_obtial))
            center_units = np.ones((1, len(way_obtial)))

            if self.obtial_type == 0:
                userful_str = [str(i+1) for i in way_obtial]
                self.program.log_window_text.insert('end',f'{center+1}->{around+1}π obtials:'+','.join(userful_str)+'\n')
            else:
                userful_str = [f'α{i+1}' if i < self.alpha_num else f'β{i+1-self.alpha_num}' for i in way_obtial]
                self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},π obtials:' + ','.join(userful_str) + '\n')
            
            all_square_sum = self.all_sauare_sum[np.newaxis, :][:, way_obtial]
            center_square_sum = self.each_square_sum[center, way_obtial]
            around_square_sum = self.each_square_sum[around, way_obtial]
            center_res = (center_square_sum / all_square_sum) ** 0.5 * center_units
            around_res = (around_square_sum / all_square_sum) ** 0.5 * around_units
            bond_order = np.sum((2 if self.obtial_type == 0 else 1) * center_res * around_res)
            bond_orders.append(bond_order)
        return bond_orders,O_obtials,V_obtials

    def get_atom_bond_levels(self, center):  # 计算某个原子与周围原子之间的键级
        bond_levels = []
        arounds=self.get_connections(center)
        self.N=len(arounds)
        cn=self.search_Normal(center) #中心原子法向量
        self.set_Normal(center,cn)
        same_O_obtials=[] #三个间之间共有的Π轨道
        same_V_obtials=[]
        for around in arounds:
            an=self.search_Normal(around)
            self.set_Normal(around,an)
            bond_level,O_obtials,V_obtials = self.get_bond_level_between_tow_atom(center, around) #bondlevel可以有一个或者两个
            same_O_obtials+=O_obtials
            same_V_obtials+=V_obtials
            bond_levels.append(bond_level)
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},bond order：{bond_level}\n')
        same_O_obtials=sorted(list(set(same_O_obtials)))
        same_V_obtials=sorted(list(set(same_V_obtials)))
        # 挑选出来的非占据轨道有很多不合理的，删去
        new_same_V_obtials=[]
        if len(same_V_obtials)>len(same_O_obtials):
            if len(same_O_obtials)>0:
                baseId=same_V_obtials[len(same_O_obtials)-1]
                baseEnergy=self.Eigenvalues[baseId]
                for each in same_V_obtials:
                    if self.Eigenvalues[each]<baseEnergy+0.05:
                        new_same_V_obtials.append(each)
            same_V_obtials=new_same_V_obtials
        self.logger.info(f'atom:{center+1},Oobtials:{[i+1 for i in sorted(same_O_obtials)]}')
        self.logger.info(f'atom:{center+1},Vobtials:{[i+1 for i in sorted(same_V_obtials)]}')
        O_center_square_sum = self.each_square_sum[center, same_O_obtials]
        O_all_square_sum = self.all_sauare_sum[np.newaxis, :][:, same_O_obtials]
        O_center_res = (O_center_square_sum / O_all_square_sum) ** 0.5 
        O_atom_charge = np.sum((2 if self.obtial_type == 0 else 1) * O_center_res * O_center_res)
        O_atom_charge_energy = np.sum((2 if self.obtial_type == 0 else 1) * O_center_res * O_center_res*self.Eigenvalues[same_O_obtials])

        V_center_square_sum = self.each_square_sum[center, same_V_obtials]
        V_all_square_sum = self.all_sauare_sum[np.newaxis, :][:, same_V_obtials]
        V_center_res = (V_center_square_sum / V_all_square_sum) ** 0.5 
        V_atom_charge = np.sum((2 if self.obtial_type == 0 else 1) * V_center_res * V_center_res)
        V_atom_charge_energy = np.sum((2 if self.obtial_type == 0 else 1) * V_center_res * V_center_res*self.Eigenvalues[same_V_obtials])
        self.program.log_window_text.insert('end', f'charge density:{O_atom_charge}\n')
        self.program.log_window_text.insert('end', f'nucleophilic energy:{O_atom_charge_energy}\n')
        self.program.log_window_text.insert('end', f'electrophilic energy:{V_atom_charge_energy}\n')
        self.program.server.set_normals(self.normals)
        return np.array(bond_levels)

    def caculate(self,centers):
        for i, center in enumerate(centers):
            self.program.log_window_text.insert('end', f'{center + 1}:\n')  # 提示原子序号
            bond_levels = self.get_atom_bond_levels(center)
            for each in bond_levels.T:
                bond_order=np.sum(each)
                self.program.log_window_text.insert('end', f'sum of bond orders:{bond_order}\n')
                base_level=self.program.config['base_level']
                atomFree=base_level-bond_order
                self.program.server.atomFree[f'{center}']=atomFree
                self.program.log_window_text.insert('end', f'free valence:{atomFree}\n')
            self.program.update_progress('计算自由价',(i+1)/len(centers))