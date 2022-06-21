import numpy as np
import math
from sqlalchemy import true
from pages.utils import posan_function,get_gridPoints,vector_angle,get_normalVector,orbital_classify,list_remove,get_changeScope\
,get_coefficients,differ_function,get_dihedralAngle,nodeNum,multiple,get_extraValue
from .. import utils
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
        self.centerGridPoints=get_gridPoints(0.1,0.01,ball=True)
        self.pass_porbitals=[]
        self.sContributs={} #记录所有分子轨道的s组分的贡献
        self.selectedorbitals={}
        self.p_vectors={} #记录p轨道方向
        self.units={} #记录成键还是反键
        self.dihedralAngles={}
        self.planVectors={}
        self.samePlanes={}
        self.ratios={} #轨道在法向量上投影的比率
        self.savedArray=[]
        self.Batch=False
        self.includeV=False
        self.orbitalElectron=2 if self.Data.orbital_type==0 else 1

    def get_Normal(self,atom_i,atom_j,loc='bond'): #对获得标量函数的封装
        if loc=='bond':
            locNum=0.001
        elif loc=='plane':
            locNum=1
        if f'{atom_i}-{atom_j}-{loc}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
            connections_i=self.Data.connections(atom_i)
            connections_j=self.Data.connections(atom_j)
            p1,p2,p3=[(self.Data.atomPos(each)-self.Data.atomPos(atom_i))*(1 if each==atom_j else locNum) for each in connections_i] #获取中心原子到三个相邻原子的法向量
            normal_vector_i=utils.get_normalVector(p1,p2,p3)
            if len(connections_j)==3:
                p1,p2,p3=[(self.Data.atomPos(each)-self.Data.atomPos(atom_j))*(1 if each==atom_j else locNum) for each in connections_j] #获取中心原子到三个相邻原子的法向量
                normal_vector_j=utils.get_normalVector(p1,p2,p3)
                if utils.vector_angle(normal_vector_i,normal_vector_j)>0.5:
                    normal_vector_j*=-1
            else:
                normal_vector_j=normal_vector_i
                self.normals[f'{atom_j}-{atom_i}-{loc}']=normal_vector_j
            self.normals[f'{atom_i}-{atom_j}-{loc}']=normal_vector_i
            print(atom_i,atom_j,loc,self.normals[f'{atom_i}-{atom_j}-{loc}'])
        return self.normals[f'{atom_i}-{atom_j}-{loc}']

    def get_samePlane(self,atom):
        if f'{atom}' not in self.samePlanes.keys():
            self.samePlanes[f'{atom}']=self.Data.samePlane(atom)
        return self.samePlanes[f'{atom}']

    # 判断两个原子之间的轨道是不是π轨道,(中心原子序号，周围原子序号，轨道序号)
    def get_dihedralAngle(self,center,around,orbital,p1,p2,p3,p4):
        key=f'{center}-{around}-{orbital}'
        if key not in self.dihedralAngles.keys():
            angle=get_dihedralAngle(p1,p2,p3,p4)
            self.dihedralAngles[key]=angle
            return angle
        else:
            return self.dihedralAngles[key]
    def get_planVector(self,center,around,centerPos,aroundPos,point):
        '''计算两原子与法向量链接中点的三个点确定的平面的法向量'''
        key=f'{center}-{around}'
        if key not in self.planVectors.keys():
            normal=get_normalVector(centerPos,aroundPos,point)
            self.planVectors[key]=normal
        return self.planVectors[key]
    def get_orbital_is_userful(self, center, around, orbital): #判断两原子之间的π轨道是不是π轨道
        orbitalName=self.Data.orbitals[orbital]
        if orbitalName[-1]=='V' and (not self.includeV):
            return False
        if self.Data.atoms[around]['atom_type']=='H':
            return False

        self.logger.info(f'*'*70)
        self.logger.info(f'center:{center+1},around:{around+1},orbital:{orbital+1}')
        all_square_sum = self.Data.all_sauare_sum[:, orbital]
        center_sContribute=(get_coefficients('SD',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_sContribute=(get_coefficients('SD',self.Data.atoms,around,orbital)/all_square_sum)[0]
        sdContribute=self.program.config['sdContribute']
        self.logger.info(f's+d orbital contribute of center:{center_sContribute:.4f},around:{around_sContribute:.4f}')
        # s的贡献不能太大
        if center_sContribute>sdContribute or around_sContribute>sdContribute:
            self.logger.info(f'err-1: s+d orbital contribute is biger than {self.program.config["sdContribute"]}')
            return False
        pContributeLimit=self.program.config["pContribute"]
        if self.program.Data.orbital_type==1:
            pContributeLimit*=2
        efficients=get_coefficients('P',self.Data.atoms,center,orbital,raw=True)
        self.logger.info(f'efficients={efficients.tolist()}')
        center_spContribute=(get_coefficients('SP',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_spContribute=(get_coefficients('SP',self.Data.atoms,around,orbital)/all_square_sum)[0]
        self.logger.info(f'sp contribution center:{center_spContribute:.4f}, around:{around_spContribute:.4f}')
        # bondOrder=self.orbitalElectron*(center_spContribute*around_spContribute)**0.5
        
        if center_spContribute<0.01 and around_spContribute<0.01:
            return False
        # if bondOrder<0.015:
        #     self.logger.info('err: contribute prod is smaller than 0.01')
        #     return False
        
        # 再判断p的贡献
        center_pContribute=(get_coefficients('P',self.Data.atoms,center,orbital)/all_square_sum)[0]
        around_pContribute=(get_coefficients('P',self.Data.atoms,around,orbital)/all_square_sum)[0]
        self.logger.info(f'p contribution center:{center_pContribute:.4f}, around:{around_pContribute:.4f}')
        
        if center_sContribute>center_spContribute or around_sContribute>around_spContribute:
            self.logger.info('err-4: s+d contribute is bigger than s+p contribute')
            return False

        centerPos=self.Data.atomPos(center).reshape(3,1)
        aroundPos=self.Data.atomPos(around).reshape(3,1)

        # 计算两原子键轴中间处的函数值，如果太大则不是π轨道
        # 去键轴上十个点，分别带入函数求得函数值
        center_paras = np.array(self.Data.standard_basis[center])
        center_ts=get_coefficients('2SP',self.Data.atoms,center,orbital,raw=True)
        around_paras = np.array(self.Data.standard_basis[around])
        around_ts=get_coefficients('2SP',self.Data.atoms,around,orbital,raw=True)

        # 计算p轨道所在的方向
        centerMaxPos,centerMaxValue=get_extraValue(centerPos,center_paras,center_ts,valueType='max')
        aroundMaxPos,aroundMaxValue=get_extraValue(aroundPos,around_paras,around_ts,valueType='max')
        centerMinPos,centerMinValue=get_extraValue(centerPos,center_paras,center_ts,valueType='min')
        aroundMinPos,aroundMinValue=get_extraValue(aroundPos,around_paras,around_ts,valueType='min')
        centerMaxVector=(centerMaxPos-centerPos).flatten()
        centerMinVector=(centerMinPos-centerPos).flatten()
        aroundMaxVector=(aroundMaxPos-aroundPos).flatten()
        aroundMinVector=(aroundMinPos-aroundPos).flatten()
        self.logger.info(f'centerMaxVector={centerMaxVector.flatten()},centerMaxValue={centerMaxValue:.6f}')
        self.logger.info(f'centerMinVector={centerMinVector.flatten()},centerMinValue={centerMinValue:.6f}')
        self.logger.info(f'aroundMaxVector={aroundMaxVector.flatten()},aroundMaxValue={aroundMaxValue:.6f}')
        self.logger.info(f'aroundMinVector={aroundMinVector.flatten()},aroundMinValue={aroundMinValue:.6f}')

        cn=self.get_Normal(center,around)
        an=self.get_Normal(around,center)
        self.logger.info(f'cn={cn.tolist()},an={an.tolist()}')
        if vector_angle(cn,an)>0.5:
            an*=-1
        if centerMaxValue==0 or aroundMaxValue==0:
            return False
        centerPVector=centerMaxVector if centerMaxValue+aroundMaxValue>0 else centerMinVector*-1
        aroundPVector=aroundMaxVector if centerMinValue+aroundMinValue>0 else aroundMinVector*-1
        centerAngle=vector_angle(centerMaxVector,cn)
        aroundAngle=vector_angle(aroundMaxVector,an)
        if (centerAngle-0.5)*(aroundAngle-0.5)>0:
            self.units[f'{center}-{around}-{orbital}']=1
        elif (centerAngle-0.5)*(aroundAngle-0.5)<0:
            self.units[f'{center}-{around}-{orbital}']=-1
        else:
            self.units[f'{center}-{around}-{orbital}']=1
        centerAngle=0.5-abs(centerAngle-0.5)
        aroundAngle=0.5-abs(aroundAngle-0.5)
        centerRatio=np.cos(centerAngle*np.pi)
        aroundRatio=np.cos(aroundAngle*np.pi)
        
        self.logger.info(f'{centerRatio=},{aroundRatio=}')
        self.ratios[f'{center}-{around}-{orbital}']=centerRatio
        self.ratios[f'{around}-{center}-{orbital}']=aroundRatio
        if centerRatio.round(6)==0 or aroundRatio.round(6)==0:
            return False
        
        center_square_sum = self.Data.squareSum(center,orbital)
        around_square_sum = self.Data.squareSum(around,orbital)
                        
        center_res = (center_square_sum / all_square_sum) ** 0.5 *centerRatio
        around_res = (around_square_sum / all_square_sum) ** 0.5 *aroundRatio
        bondOrder=(self.Data.orbitalElectron*center_res*around_res).sum()
        self.logger.info(f'{bondOrder=}')
        if bondOrder<0.001:
            return False


        # if centerMaxValue<0.03 and aroundMaxValue>0.03:
        #         self.units[f'{center}-{around}-{orbital}']=-1
        #         self.logger.info('node point')
        #         return True
        # if max([centerMaxValue,-centerMinValue])<0.03 or max([aroundMaxValue,-aroundMinValue])<0.03:
        #     return False
        # self.logger.info(f'dihedralAngle={self.get_dihedralAngle(center,around,orbital,centerMaxPos.flatten(),centerPos.flatten(),aroundPos.flatten(),aroundMaxPos.flatten())}')

        if np.linalg.norm(centerMaxVector)<=0.001 or np.linalg.norm(centerMaxVector)<=0.001:
            return False
            pass
        
        # self.p_vectors[f'{center}-{orbital}']=c_pv
        # self.p_vectors[f'{around}-{orbital}']=a_pv

        # self.logger.info(f'max wave function value of center:{c_value:.4f},around:{a_value:.4f},and they should bigger pPosanValue {self.program.config["pPosanValue"]}')
       
        
        # if self.N==2:
        #     pbAngle=self.program.config["pbAngle"]
        #     self.logger.info(f'the ange between p orbital and bond of center:{c_angle},around:{a_angle},and they should in the range of 0.5+-{pbAngle}')
        #     if max([abs(c_angle-0.5),abs(a_angle-0.5)])>pbAngle or min([c_value,a_value])<self.program.config["pPosanValue"]:
        #         self.logger.info(f'err-6: p orbital vector is not verpendicular to bond')
        #         return False
        #     else:
        #         self.logger.info('this molecular orbital is sp orbital')
        #         return True
        if self.N==3:
            center_normal=cn.reshape(3,1)
            around_normal=an.reshape(3,1)
            if vector_angle(cn,an)>0.5:
                around_normal*=-1
            between_up=(centerPos+center_normal+aroundPos+around_normal)/2
            between_down=(centerPos-center_normal+aroundPos-around_normal)/2
            # 求出过与中心原子相连的三个原子的平面的法向量
            
            # cn_plane=self.get_Normal(center,around,loc='plane')
            # self.logger.info(f'{cn=},{cn_plane=}')
            # bias=vector_angle(cn,cn_plane,trans=True)
            # self.logger.info(f'{bias=}')
            # cnp_angle=vector_angle(cn,c_pv,trans=True) #p轨道方向和法向量方向的夹角
            # anp_angle=vector_angle(an,a_pv,trans=True)
            # self.logger.info(f'the angle between p orbital direction and normal vector of center is {cnp_angle:.4f} around is {anp_angle:.4f}')
            # if cnp_angle<0.1 and anp_angle<0.1:
            #     self.logger.info('right the angle between p orbital direction and normal vector small than 0.1')
            #     return True
            centerPlaneVector=self.get_planVector(center,around,centerPos.flatten(),aroundPos.flatten(),(centerPos+center_normal).flatten()) #键轴三角面的法向量
            aroundPlaneVector=self.get_planVector(around,center,aroundPos.flatten(),centerPos.flatten(),(aroundPos+around_normal).flatten())
            centerPlanAngle=0.5-vector_angle(centerPlaneVector,centerPVector,trans=True)
            aroundPlanAngle=0.5-vector_angle(aroundPlaneVector,aroundPVector,trans=True)
            normalAngle=vector_angle(cn,an,trans=True)
            self.logger.info(f'{centerPlanAngle=},{aroundPlanAngle=}')
            centerNormalValue=posan_function(centerPos,centerPos+center_normal*0.1,center_paras,center_ts).item()
            aroundNormalValue=posan_function(aroundPos,aroundPos+around_normal*0.1,around_paras,around_ts).item()
            self.logger.info(f'{centerNormalValue=},{aroundNormalValue=}')
            # if centerNormalValue*aroundNormalValue>0:
            #     self.units[f'{center}-{around}-{orbital}']=1
            # elif centerNormalValue*aroundNormalValue<0:
            #     self.units[f'{center}-{around}-{orbital}']=-1
            # else:
            #     self.units[f'{center}-{around}-{orbital}']=0

            # 节点
            # if centerMaxValue<0.01 and aroundMaxValue>0.01 and aroundPlanAngle<0.21 :
            #     self.units[f'{center}-{around}-{orbital}']=0
            #     return True
            # if aroundMaxValue<0.01 and centerMaxValue>0.01 and centerPlanAngle<0.21 :
            #     self.units[f'{center}-{around}-{orbital}']=0
            #     return True
            
            # if (centerPlanAngle>0.21 or aroundPlanAngle>0.21) and centerPlanAngle+aroundPlanAngle>0.3:
            #     self.logger.info('p orbital on plane')
            #     return False
            # if cnp_angle>0.25 or anp_angle>0.25:
            #     # dihedralAngle=get_dihedralAngle(centerMaxPos.flatten(),centerPos.flatten(),aroundPos.flatten(),aroundMaxPos.flatten())
            #     # self.logger.info(f'{dihedralAngle=}')
            #     self.logger.info('p orbital on plane')
            #     return False
            
            
            # 这些都是叠加前的

            # self.logger.info(f'{center_normal=},{around_normal=}')
            select_upPos=np.concatenate([centerPos+center_normal,between_up,aroundPos+around_normal],axis=1)
            select_downPos=np.concatenate([centerPos-center_normal,between_down,aroundPos-around_normal],axis=1)
            self.logger.info(f'select_upPos:\n{select_upPos.round(4).tolist()}\nselect_downPos:\n{select_downPos.round(4).tolist()}')
            bondCenterPos=(centerPos+aroundPos)/2
            # 看上面连线和下面连线的函数值
            upLinePos=((aroundPos+around_normal)-(centerPos+center_normal))*np.linspace(0,1,20)+(centerPos+center_normal)
            downLinePos=((aroundPos-around_normal)-(centerPos-center_normal))*np.linspace(0,1,20)+(centerPos-center_normal)
            verticalLinePos=(between_up-between_down)*np.linspace(0,1,20)+between_down

            # if vector_angle(cn,an,trans=True)<0.1:
            #     samePlanes=self.get_samePlane(center)
            # else:
            #     samePlanes=[center,around]
            # self.logger.info(f'{samePlanes=}')
           
            upLineValues=utils.multiFunction(orbital,[center,around],upLinePos,self.Data)
            downLineValues=utils.multiFunction(orbital,[center,around],downLinePos,self.Data)
            verticalLineValues=utils.multiFunction(orbital,[center,around],verticalLinePos,self.Data)

            self.logger.info(f'upLineValues={upLineValues.tolist()}')
            self.logger.info(f'downLineValues={downLineValues.tolist()}')
            self.logger.info(f'verticalLineValues={verticalLineValues.tolist()}')
            # if abs(multiple(verticalLineValues[0],verticalLineValues[-1]))>5:
            #     return False
            # if upLineValues[0]*downLineValues[0]>0 or upLineValues[-1]*downLineValues[-1]>0:
            #     return False
            
            upNodeNum=nodeNum(upLineValues)
            downNodeNum=nodeNum(downLineValues)
            verticalNodeNum=nodeNum(verticalLineValues)
            self.logger.info(f'{upNodeNum=},{downNodeNum=},{verticalNodeNum=}')
            # if upNodeNum==0 and downNodeNum==0 and verticalNodeNum>0: # 成键轨道
            #     # self.units[f'{center}-{around}-{orbital}']=1
            #     return True
            # elif upNodeNum>0 and downNodeNum>0:
            #     # self.units[f'{center}-{around}-{orbital}']=-1
            #     return True
            # else:
            #     return False
            return True
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
                self.program.log_window_text.insert('end',f'{around_units.flatten().tolist()}\n')
                
                all_square_sum = self.Data.all_sauare_sum[:, way_orbital]
                # center_square_sum = self.Data.each_square_sum[center, way_orbital]
                # around_square_sum = self.Data.each_square_sum[around, way_orbital]
                centerRatios=np.array([self.ratios[f'{center}-{around}-{orbital}'] for orbital in way_orbital])
                aroundRatios=np.array([self.ratios[f'{around}-{center}-{orbital}'] for orbital in way_orbital])
                self.logger.info(f'centerRatiosSum:{centerRatios.sum()},{centerRatios.sum()/len(centerRatios)}')
                self.logger.info(f'aroundRatiosSum:{aroundRatios.sum()},{aroundRatios.sum()/len(aroundRatios)}')
                self.logger.info(f'RatiosSum:{(centerRatios.sum()+aroundRatios.sum())},{(centerRatios.sum()+aroundRatios.sum())/(len(centerRatios)+len(aroundRatios))}')
                self.program.log_window_text.insert('end',f'centerRatios:{centerRatios.round(4).flatten().tolist()}\n')
                self.program.log_window_text.insert('end',f'aroundRatios:{aroundRatios.round(4).flatten().tolist()}\n')
                self.logger.info(f'centerRatios:{centerRatios.round(4).flatten().tolist()}')
                self.logger.info(f'aroundRatios:{aroundRatios.round(4).flatten().tolist()}')
                center_square_sum = self.Data.squareSum(center,way_orbital)
                around_square_sum = self.Data.squareSum(around,way_orbital)
                
                center_res = (center_square_sum / all_square_sum) ** 0.5 *centerRatios
                around_res = (around_square_sum / all_square_sum) ** 0.5 *aroundRatios
                self.logger.info(f'orders:{center_res * around_res}')
                self.program.log_window_text.insert('end',f'orbitalOrders:{(center_res*around_res).round(4).flatten().tolist()}\n')
                # self.program.log_window_text.insert('end',f'aroundRes:{around_res.round(4).flatten().tolist()}\n')
                bond_order = np.sum((2 if self.Data.orbital_type == 0 else 1) * center_res * center_units * around_res* around_units)

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
            # cn=self.get_Normal(center,around)
            # an=self.get_Normal(around,center)
            bond_order,O_orbitals,V_orbitals = self.get_bond_order_between_tow_atom(center, around) #bondlevel可以有一个或者两个
            same_O_orbitals+=O_orbitals
            same_V_orbitals+=V_orbitals
            bond_orders.append(bond_order)
            # bond_order=list_remove(bond_order,0)
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},bond order:{bond_order[0]:.4f},bond length:{self.Data.bondLength(center,around):.4f}\n')
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
        # self.logger.info(f'atom:{center+1},Oorbitals:{[i+1 for i in sorted(same_O_orbitals)]}')
        # self.logger.info(f'atom:{center+1},Vorbitals:{[i+1 for i in sorted(same_V_orbitals)]}')

        O_center_square_sum=get_coefficients('P',self.Data.atoms,center,same_O_orbitals)
        O_all_square_sum = self.Data.all_sauare_sum[:, same_O_orbitals]
        O_center_res = (O_center_square_sum / O_all_square_sum) ** 0.5 
        # self.logger.info(f'O orbital coefficients：{O_center_res}')
        O_atom_charge = np.sum((2 if self.Data.orbital_type == 0 else 1) * O_center_res * O_center_res)
        O_atom_charge_energy = np.sum((2 if self.Data.orbital_type == 0 else 1) * O_center_res * O_center_res*self.Data.Eigenvalues[same_O_orbitals])

        V_center_square_sum=get_coefficients('P',self.Data.atoms,center,same_V_orbitals)
        
        V_all_square_sum = self.Data.all_sauare_sum[:, same_V_orbitals]
        V_center_res = (V_center_square_sum / V_all_square_sum) ** 0.5 
        # self.logger.info(f'V orbital coefficients：{V_center_res}')
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
    
    def select(self,centers): #程序先进行自己的判断与选择
        for center in centers:
            arounds=self.Data.connections(center)
            self.N=len(arounds)
            for around in arounds:
                O_orbitals,V_orbitals=self.get_orbital_between_atoms(center,around)
                self.selectedorbitals[f'{center}-{around}-O']=O_orbitals
                self.selectedorbitals[f'{center}-{around}-V']=V_orbitals
        res=self.selectedorbitals
        all_orbitals=self.program.Data.atoms[0]['orbitals']
        for key in res.keys():
            center=int(key.split('-')[0])+1
            around=int(key.split('-')[1])+1
            orbitalType=key.split('-')[2]
            if orbitalType=='O':
                if self.program.Data.orbital_type==0:
                    self.program.log_window_text.insert('end',f'{center}->{around}:'+','.join(f'{each+1}' for each in res[key])+'\n')

                elif self.program.Data.orbital_type==1:
                    #将轨道分为两种类型
                    Aorbitals=[]
                    Borbitals=[]
                    for each in res[key]:
                        if each<len(all_orbitals)/2:
                            Aorbitals.append(each)
                        else:
                            Borbitals.append(each)
                    self.program.log_window_text.insert('end',f'{center}->{around}α:'+','.join(f'{each+1}' for each in Aorbitals)+'\n')
                    self.program.log_window_text.insert('end',f'{center}->{around}β:'+','.join(f'{each+1-len(all_orbitals)//2}' for each in Borbitals)+'\n')
        return self.selectedorbitals