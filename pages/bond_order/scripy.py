from cv2 import sepFilter2D
import numpy as np
import math
from pages.utils import posan_function,get_gridPoints,vector_angle,get_normalVector,orbital_classify,list_remove,get_changeScope\
,get_coefficients

class Caculater:
    def __init__(self, program):
        self.program = program
        self.Data=self.program.Data
        self.logger=program.logger
        self.normals={} # 计算每个原子的法向量
        self.pvectors={}
        self.searched=[] #记录已经搜索的原子
        self.gridPoints=get_gridPoints(1,0.05,ball=True)
        self.gridPointsBox=get_gridPoints(2,0.1,ball=True)
        self.pass_porbitals=[]
        self.sContributs={} #记录所有分子轨道的s组分的贡献
        self.selectedorbitals={}
        self.p_vectors={} #记录p轨道方向
        self.units={} #记录成键还是反键
        self.savedArray=[]
        self.Batch=False

    def get_Normal(self,atom,to): #对获得标量函数的封装
        if f'{atom}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            atomPos=self.Data.atomPos(atom)
            connections=self.Data.connections(atom)
            p1,p2,p3=[(self.Data.atomPos(each)-atomPos)*(1 if each==to else 1) for each in connections]
            n=get_normalVector(p1,p2,p3)
            self.normals[f'{atom}-{to}']=n
            
        return self.normals[f'{atom}-{to}']

    def search_Normal(self,atom,to):
        connections=self.Data.connections(atom) # 该原子连接的原子
        if len(connections)==3:
            n=self.get_Normal(atom,to)
        else:
            n=self.get_Normal(to,atom)
        self.logger.info(f'normal vector from={atom+1},to={to+1},{n}')
        return n
    # 判断两个原子之间的轨道是不是π轨道,(中心原子序号，周围原子序号，轨道序号)
    

    def get_orbital_is_userful(self, center, around, orbital): #判断两原子之间的π轨道是不是π轨道
        if self.Data.atoms[around]['atom_type']=='H':
            return False

        self.logger.info(f'*'*70)
        self.logger.info(f'center:{center+1},around:{around+1},orbital:{orbital+1}')
        all_square_sum = self.Data.all_sauare_sum[:, orbital]
        center_sContribute=(get_coefficients('SD',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_sContribute=(get_coefficients('SD',self.Data.atoms,around,orbital)/all_square_sum)[0]
        sdContribute=self.program.config['sdContribute']
        self.logger.info(f's+d orbital contribute of center:{center_sContribute:.4f},around:{around_sContribute:.4f}')
        if center_sContribute>sdContribute or around_sContribute>sdContribute:
            self.logger.info(f'err-1: s+d orbital contribute is biger than {self.program.config["sdContribute"]}')
            return False
        
        center_spContribute=(get_coefficients('SP',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_spContribute=(get_coefficients('SP',self.Data.atoms,around,orbital)/all_square_sum)[0]
        self.logger.info(f'sp contribution center:{center_spContribute:.4f}, around:{around_spContribute:.4f}')
        if center_spContribute <= self.program.config["pContribute"] or around_spContribute <= self.program.config["pContribute"]:
            self.logger.info(f'err-2: sp contribute is smaller than {self.program.config["pContribute"]}')
            return False # 判断条件1，s轨道的数值太小的排除
        
        # 再判断p的贡献
        center_pContribute=(get_coefficients('SP',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_pContribute=(get_coefficients('SP',self.Data.atoms,around,orbital)/all_square_sum)[0]
        self.logger.info(f'p contribution center:{center_pContribute:.4f}, around:{around_pContribute:.4f}')
        if center_pContribute <= self.program.config["pContribute"]/2 or around_pContribute <= self.program.config["pContribute"]/2:
            self.logger.info(f'err-3: p contribute is smaller than {self.program.config["pContribute"]/2}')
            return False # 判断条件1，s轨道的数值太小的排除

        if center_sContribute>center_spContribute or around_sContribute>around_spContribute:
            self.logger.info('err-4: s+d contribute is bigger than s+p contribute')
            return False

        centerPos=self.Data.atomPos(center).reshape(3,1)
        aroundPos=self.Data.atomPos(around).reshape(3,1)

        bondLength=np.linalg.norm(aroundPos-centerPos)
        self.logger.info(f'bondLength={bondLength}')
        # 计算两原子键轴中间处的函数值，如果太大则不是π轨道
        # 去键轴上十个点，分别带入函数求得函数值
        center_paras = np.array(self.Data.standard_basis[center])
        center_ts=get_coefficients('P',self.Data.atoms,center,orbital,raw=True)
        around_paras = np.array(self.Data.standard_basis[around])
        around_ts=get_coefficients('P',self.Data.atoms,around,orbital,raw=True)

        #将两原子键轴中点的函数值保存在文件中
        # bondGrid=(centerPos+aroundPos)/2+self.gridPointsBox
        # centerArray=posan_function(centerPos,bondGrid,center_paras[:,0],center_paras[:,2],center_ts)
        # aroundArray=posan_function(aroundPos,bondGrid,around_paras[:,0],around_paras[:,2],around_ts)
        # self.saveArray(f'datas//{center+1}-{around+1}-{orbital+1}',np.concatenate([bondGrid,centerArray+aroundArray]).T)


        # 计算p轨道所在的方向 (下面都是原本属于N==2是的内容)
        cvs=posan_function(centerPos,centerPos+self.gridPoints,center_paras[:,0],center_paras[:,2],center_ts) # center values
        avs=posan_function(aroundPos,aroundPos+self.gridPoints,around_paras[:,0],around_paras[:,2],around_ts)

        c_maxID=np.argmax(cvs)
        a_maxID=np.argmax(avs)
        c_pv=self.gridPoints[:,c_maxID] # 中心原子p轨道的方向 center p orbital vector
        a_pv=self.gridPoints[:,a_maxID] # 邻接原子p轨道的方向
        self.logger.info(f'p orbital vectors center:{[round(each,3) for each in c_pv]}, around:{[round(each,3) for each in a_pv]}')
        
        self.p_vectors[f'{center}-{orbital}']=c_pv
        self.p_vectors[f'{around}-{orbital}']=a_pv


        b_vector=aroundPos-centerPos # 键轴的向量
        c_pvs=c_pv.reshape(3,1)/np.linalg.norm(c_pv)*np.arange(0.1,3.0,0.1)[np.newaxis,:] #center p orbital vectors
        cpvvs=posan_function(centerPos,centerPos+c_pvs,center_paras[:,0],center_paras[:,2],center_ts) #center p orbital vector values
        if np.max(cpvvs)*np.min(cpvvs)<0:
            self.logger.info('err-5: there are cross profile in p orbital way') #p轨道方向有节点
            return False
        c_angle,a_angle=vector_angle(c_pv,b_vector),vector_angle(a_pv,b_vector) #p轨道与键轴的夹角
        c_value,a_value=np.max(cvs),np.max(avs)

        # self.logger.info(f'max wave function value of center:{c_value:.4f},around:{a_value:.4f},and they should bigger pPosanValue {self.program.config["pPosanValue"]}')
       
        self.pvectors[f'{center}-{orbital}']=c_pv  #只有连接数是2的时候法向量为
        self.pvectors[f'{around}-{orbital}']=a_pv
        M=len(self.Data.connections(around))
        
        if self.N==2:
            pbAngle=self.program.config["pbAngle"]
            self.logger.info(f'the ange between p orbital and bond of center:{c_angle},around:{a_angle},and they should in the range of 0.5+-{pbAngle}')
            if max([abs(c_angle-0.5),abs(a_angle-0.5)])>pbAngle or min([c_value,a_value])<self.program.config["pPosanValue"]:
                self.logger.info(f'err-6: p orbital vector is not verpendicular to bond')
                return False
            else:
                self.logger.info('this molecular orbital is sp orbital')
                return True
        elif self.N==3:
            # 求出过与中心原子相连的三个原子的平面的法向量
            cn=self.normals[f'{center}-{around}']
            an=self.normals[f'{around}-{center}']
            
            cnp_angle=vector_angle(cn,c_pv,trans=True) #p轨道方向和法向量方向的夹角
            anp_angle=vector_angle(an,a_pv,trans=True)
            self.logger.info(f'the angle between p orbital direction and normal vector of center is {cnp_angle:.4f} around is {anp_angle:.4f}')

            # 计算两原子法向量中心处的函数值变化率
            center_normal=cn.reshape(3,1)
            around_normal=an.reshape(3,1)
            if vector_angle(cn,an)>0.5:
                around_normal*=-1
            between_up=(centerPos+center_normal+aroundPos+around_normal)/2
            between_down=(centerPos-center_normal+aroundPos-around_normal)/2
            between_up_before=posan_function(centerPos,between_up,center_paras[:,0],center_paras[:,2],center_ts)
            between_down_before=posan_function(centerPos,between_down,center_paras[:,0],center_paras[:,2],center_ts)
            between_up_after=posan_function(aroundPos,between_up,center_paras[:,0],center_paras[:,2],center_ts)+between_up_before
            between_down_after=posan_function(aroundPos,between_down,center_paras[:,0],center_paras[:,2],center_ts)+between_down_before
            between_up_change=abs(between_up_after**2-between_up_before**2).item()
            between_down_change=abs(between_down_after**2-between_down_before**2).item()
            self.logger.info(f'{between_up_change=},{between_down_change=}')
            if min([between_up_change,between_down_change])<self.program.config['betweenChange']:
                return False

            if M!=4:
                self.logger.info(f'{M=}')
                if anp_angle>self.program.config['pbAngle']: #周围原子必须与法向量平行
                    self.logger.info(f'err-7: normal not parallel to p')
                    return False
                connections=self.Data.connections(center).copy()
                connections.remove(around)
                connect_vectors=[self.Data.bondVector(each,center) for each in connections]
                connect_angles=[vector_angle(each,c_pv,trans=True) for each in connect_vectors]
                Angels=connect_angles+[cnp_angle] # 包含法向量与2p轨道夹角
                self.logger.info(f'{Angels=}')
                if min(connect_angles)<self.program.config['pnAngle'] or cnp_angle<self.program.config['pbAngle']: # 所有夹角的最小值要小于一定值(0.2)
                    if np.argmin(Angels)!=len(Angels)-1: # 如果最小值不是最后一位,中心原子的法向量是C-R方向
                        self.logger.info('center 2p direction on bond')
                        # 计算周围原子叠加前后的波函数值的变化，判断成键反键或者是不是π轨道
                        center_up_value=posan_function(centerPos,aroundPos+c_pv.reshape(3,1),center_paras[:,0],center_paras[:,2],center_ts)
                        center_down_value=posan_function(centerPos,aroundPos-c_pv.reshape(3,1),center_paras[:,0],center_paras[:,2],center_ts)
                        around_up_value=posan_function(aroundPos,aroundPos+c_pv.reshape(3,1),center_paras[:,0],center_paras[:,2],center_ts)
                        around_down_value=posan_function(aroundPos,aroundPos-c_pv.reshape(3,1),center_paras[:,0],center_paras[:,2],center_ts)
                        up_overlap_value=center_up_value+around_up_value
                        down_overlap_value=center_down_value+around_down_value
                        if (up_overlap_value**2-around_up_value**2)>0 and (down_overlap_value**2-around_down_value**2)>0:
                            self.units[f'{center}-{around}-{orbital}']=1
                            return True
                        elif (up_overlap_value**2-around_up_value**2)<0 and (down_overlap_value**2-around_down_value**2)<0:
                            self.units[f'{center}-{around}-{orbital}']=-1
                            return True
                        else:
                            self.logger.info('err-8: not increase or decrease at the same time')
                            return False
                    else:
                        self.logger.info(f'')
                        return True
                else:
                    self.logger.info(f'err-9:all angle is too big ')
                    return False
            elif M==4: #周围原子连接四个原子，sp3杂化
                self.logger.info(f'{M=}')
                center_connections=self.Data.connections(center).copy()
                center_connections.remove(around)
                center_connect_vectors=[self.Data.bondVector(each,center) for each in center_connections]
                center_connect_angles=[vector_angle(each,c_pv,trans=True) for each in center_connect_vectors]
                around_connections=self.Data.connections(around).copy()
                around_connections.remove(center)
                around_connect_vectors=[self.Data.bondVector(each,around) for each in around_connections]
                around_connect_angles=[vector_angle(each,a_pv,trans=True) for each in around_connect_vectors]
                self.logger.info(f'{center_connect_angles=},{around_connect_angles=}')
                self.logger.info(f'{anp_angle=}')

                
                
                # 中心原子可以是法向量或者键轴方向，相邻原子需要时法向量方向，但范围可以放宽
                bondVector=self.Data.bondVector(around,center) #键轴向量
                pbAngle=vector_angle(bondVector,c_pv) #键轴与p轨道的夹角
                self.logger.info(f'{pbAngle=}')
                if pbAngle>0.2 and anp_angle<self.program.config['pnAngleM4']:
                    return True
                if cnp_angle<self.program.config['pnAngle'] and anp_angle<self.program.config['pnAngleM4']: #中心原子必须与法向量平行
                    self.logger.info(f'yes-N3M4-1')
                    return True
                if min(center_connect_angles)<self.program.config['pnAngle'] and anp_angle<self.program.config['pnAngleM4']: #周围原子平行于键轴
                    self.logger.info(f'yes-N3M4-2')
                    return True
                else:
                    self.logger.info(f'err-12: around bonds not parallel to p')
                    return False
        else:
            self.logger.info(f'err-10: center atom connection number not equal to 2 or 3 which is {self.N}')
            return False

    def get_orbital_between_atoms(self, center, around):  # 挑选两个原子之间π键有哪些
        orbital_num = self.Data.orbital_length
        O_orbitals=[]
        V_orbitals=[]
        
        # 计算与中心原子法向量与所有周围原子键轴的夹角

        for orbital in range(orbital_num):  # 所有的O轨道都判断
            orbitalName=self.Data.orbitals[orbital]
            res = self.get_orbital_is_userful(center,around,orbital)
            if res is None:
                raise f'{center=},{around=},{orbital=}'
            if orbitalName[-1]=='O':
                if res:
                    O_orbitals.append(orbital)
            elif orbitalName[-1]=='V':
                
                if res:
                    V_orbitals.append(orbital)
            else:
                raise Exception(f'unkonw:{orbitalName},{orbitalName[-1]}')
            self.program.update_progress(f'{center+1}-{around+1}',(orbital+1)/orbital_num)
        return O_orbitals,V_orbitals


    def get_unit(self, center, around, orbital):  # 判断两原子之间的正负关系\
        if f'{center}-{around}-{orbital}' in self.units.keys():
            return self.units[f'{center}-{around}-{orbital}']
        # 根据两原子p轨道的夹角计算
        c_nv,a_nv=self.normals[f'{center}-{around}'],self.normals[f'{around}-{center}']
        if vector_angle(c_nv,a_nv)>0.5:
            a_nv*=-1
        c_pv,a_pv=self.p_vectors[f'{center}-{orbital}'],self.p_vectors[f'{around}-{orbital}']
        if (0.6-vector_angle(c_nv,c_pv))*(0.6-vector_angle(a_nv,a_pv))>0: #
            return 1
        else:
            return -1
        capAngle=vector_angle(c_pv,a_pv)
        self.logger.info(f'{center+1},{around+1},{orbital+1},the angle between 2 atoms 2p orbital is {capAngle}')
        if capAngle<0.75:
            return 1
        elif capAngle>=0.75:
            return  -1
        else:
            raise f'wrongAngle between center and around p orbitals{capAngle}'


    def get_bond_order_between_tow_atom(self, center, around):  # 计算两个原子之间两个方向的键级（平面分子只有一个，线性分子有两个，分别用V和H表示）
        keys=self.selectedorbitals.keys()
        if f'{center}-{around}-O' in keys and f'{center}-{around}-V' in keys:
            O_orbitals,V_orbitals=self.selectedorbitals[f'{center}-{around}-O'],self.selectedorbitals[f'{center}-{around}-V']
        else:
            O_orbitals,V_orbitals=self.get_orbital_between_atoms(center,around)
        self.logger.info(f'{center=},{around=},{O_orbitals=},{V_orbitals=}')
        if self.Batch:
            self.program.log_window_text.insert('end',f'O_orbitals={[each+1 for each in O_orbitals]},V_orbitals{[each+1 for each in V_orbitals]}\n')
        bond_orders=[]
        if self.N==3:
            way_orbitals=[O_orbitals,[]]
        elif self.N==2:
            Vo,Ho=orbital_classify(center,self.pvectors,O_orbitals)
            self.logger.info(f'center:{center+1}->{around+1},Vo={[each +1 for each in Vo]}\nHo={[each +1 for each in Ho]}')
            way_orbitals=[Vo,Ho]
        else:
            raise Exception(f'N=={self.N}，连接数量错误')
        for index,way_orbital in enumerate(way_orbitals): # 两个way
            if len(way_orbital)!=0:
                around_units = [self.get_unit(center, around, orbital) for orbital in way_orbital] # 周围原子与中心原子之间的正负系数
                self.logger.info(f'center:{center+1},aroudn:{around+1},units:{around_units}')
                around_units = np.array(around_units).reshape(1, len(way_orbital))
                center_units = np.ones((1, len(way_orbital)))

                
                all_square_sum = self.Data.all_sauare_sum[:, way_orbital]
                center_square_sum = self.Data.each_square_sum[center, way_orbital]
                around_square_sum = self.Data.each_square_sum[around, way_orbital]
                center_res = (center_square_sum / all_square_sum) ** 0.5 * center_units
                around_res = (around_square_sum / all_square_sum) ** 0.5 * around_units
                bond_order = np.sum((2 if self.Data.orbital_type == 0 else 1) * center_res * around_res)

                bond_orders.append(bond_order)
            else:
                bond_orders.append(0)
        return bond_orders,O_orbitals,V_orbitals

    def get_atom_bond_orders(self, center):  # 计算某个原子与周围原子之间的键级
        bond_orders = []
        arounds=self.Data.connections(center)
        self.N=len(arounds)
        
        same_O_orbitals=[] #三个间之间共有的Π轨道
        same_V_orbitals=[]
        for around in arounds:
            cn=self.search_Normal(center,around) #中心原子法向量
            self.normals[f'{center}-{around}']=cn
            an=self.search_Normal(around,center)
            self.normals[f'{around}-{center}']=an
            # 中心原子与周围原子键轴的夹角
            nbAngles=vector_angle(cn,self.Data.bondVector(around,center),trans=True)
            self.logger.info(f'{center=},{around=},{nbAngles=}')
            bond_order,O_orbitals,V_orbitals = self.get_bond_order_between_tow_atom(center, around) #bondlevel可以有一个或者两个
            same_O_orbitals+=O_orbitals
            same_V_orbitals+=V_orbitals
            bond_orders.append(bond_order)
            bond_order=list_remove(bond_order,0)
            if len(bond_order)>0:
                self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},bond order:{",".join([f"{each:.4f}" for each in bond_order])}\n')
        same_O_orbitals=sorted(list(set(same_O_orbitals)))
        same_V_orbitals=sorted(list(set(same_V_orbitals)))
        # 挑选出来的非占据轨道有很多不合理的，删去
        new_same_V_orbitals=[]
        if len(same_V_orbitals)>len(same_O_orbitals):
            if len(same_O_orbitals)>0:
                baseId=same_V_orbitals[len(same_O_orbitals)-1]
                baseEnergy=self.Data.Eigenvalues[baseId]
                for each in same_V_orbitals:
                    if self.Data.Eigenvalues[each]<baseEnergy+0.05:
                        new_same_V_orbitals.append(each)
            same_V_orbitals=new_same_V_orbitals
        self.logger.info(f'atom:{center+1},Oorbitals:{[i+1 for i in sorted(same_O_orbitals)]}')
        self.logger.info(f'atom:{center+1},Vorbitals:{[i+1 for i in sorted(same_V_orbitals)]}')

        O_center_square_sum=get_coefficients('P',self.Data.atoms,center,same_O_orbitals)
        O_all_square_sum = self.Data.all_sauare_sum[:, same_O_orbitals]
        O_center_res = (O_center_square_sum / O_all_square_sum) ** 0.5 
        self.logger.info(f'O orbital coefficients：{O_center_res}')
        O_atom_charge = np.sum((2 if self.Data.orbital_type == 0 else 1) * O_center_res * O_center_res)
        O_atom_charge_energy = np.sum((2 if self.Data.orbital_type == 0 else 1) * O_center_res * O_center_res*self.Data.Eigenvalues[same_O_orbitals])

        V_center_square_sum=get_coefficients('P',self.Data.atoms,center,same_V_orbitals)
        
        V_all_square_sum = self.Data.all_sauare_sum[:, same_V_orbitals]
        V_center_res = (V_center_square_sum / V_all_square_sum) ** 0.5 
        self.logger.info(f'V orbital coefficients：{V_center_res}')
        # V_atom_charge = np.sum((2 if self.Data.orbital_type == 0 else 1) * V_center_res * V_center_res)
        V_atom_charge_energy = np.sum((2 if self.Data.orbital_type == 0 else 1) * V_center_res * V_center_res*self.Data.Eigenvalues[same_V_orbitals])
        self.program.log_window_text.insert('end', f'charge density:{O_atom_charge:.4f}\n')
        self.program.log_window_text.insert('end', f'nucleophilic energy:{O_atom_charge_energy:.4f}\n')
        self.program.log_window_text.insert('end', f'electrophilic energy:{V_atom_charge_energy:.4f}\n')
        self.program.server.set_normals(self.normals)
        return np.array(bond_orders)

    def caculate(self,centers):
        for i, center in enumerate(centers):
            self.program.log_window_text.insert('end', f'{center + 1}:\n')  # 提示原子序号
            bond_orders = self.get_atom_bond_orders(center)
            if bond_orders.ndim==1:
                bond_orders=bond_orders[:,np.newaxis]
            bond_order=np.sum(bond_orders,axis=0)
            show_bond_order=list(bond_order)
            show_bond_order=list_remove(show_bond_order,0)
            self.program.log_window_text.insert('end', f'sum of bond orders:{",".join([f"{each:.4f}" for each in show_bond_order])}\n')
            baseOrder=self.program.config['baseOrder']
            atomFree=list(baseOrder-bond_order)
            atomFree=list_remove(atomFree,baseOrder)
            self.program.server.atomFree[f'{center}']=atomFree #一个列表
            self.program.log_window_text.insert('end', f'free valence:{",".join([f"{each:.4f}" for each in atomFree])}\n')
            self.program.update_progress('计算自由价',(i+1)/len(centers))
    
    def select(self,centers):
        for center in centers:
            arounds=self.Data.connections(center)
            self.N=len(arounds)
            for around in arounds:
                self.normals[f'{center}-{around}']=self.search_Normal(center,around)
                self.normals[f'{around}-{center}']=self.search_Normal(around,center)
                O_orbitals,V_orbitals=self.get_orbital_between_atoms(center,around)
                self.selectedorbitals[f'{center}-{around}-O']=O_orbitals
                self.selectedorbitals[f'{center}-{around}-V']=V_orbitals
        return self.selectedorbitals