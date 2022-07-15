import numpy as np
import math
from pages.utils import get_normalVector
from .. import utils
class Caculater:
    def __init__(self, program):
        self.program = program
        self.Data=self.program.Data
        self.logger=program.logger
        self.normals={} # 计算每个原子的法向量
        self.pvectors={}
        self.pass_porbitals=[]
        self.p_vectors={} #记录p轨道方向
        self.units={} #记录成键还是反键
        self.planVectors={}
        self.samePlanes={}
        self.orders={}
        self.Batch:bool=False
        self.orbitalElectron=2 if self.Data.orbitalType==0 else 1

    def get_Normal(self,atom_i,atom_j): #对获得标量函数的封装
        locNum=0.001
        if f'{atom_i}-{atom_j}' not in self.normals.keys(): # 每个原子的法向量应该只计算一次
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
                self.normals[f'{atom_j}-{atom_i}']=normal_vector_j
            self.normals[f'{atom_i}-{atom_j}']=normal_vector_i
            print(f'{atom_i+1},{atom_j+1},{normal_vector_i}')
        return self.normals[f'{atom_i}-{atom_j}']


    def get_planVector(self,center,around,centerPos,aroundPos,point):
        '''计算两原子与法向量链接中点的三个点确定的平面的法向量'''
        key=f'{center}-{around}'
        if key not in self.planVectors.keys():
            normal=get_normalVector(centerPos,aroundPos,point)
            self.planVectors[key]=normal
        return self.planVectors[key]
    
    def get_orbitalOrder(self, center, around, orbital): 
        '''计算两个原子间每个轨道的键级'''
        if self.Data.atoms[around]['atom_type']=='H':
            return False

        self.logger.info(f'*'*70)
        self.logger.info(f'center:{center+1},around:{around+1},orbital:{orbital+1}')

        centerPos=self.Data.atomPos(center)
        aroundPos=self.Data.atomPos(around)
        bondVector=aroundPos-centerPos
        centerNormal=self.get_Normal(center,around)
        aroundNormal=self.get_Normal(around,center)
        if utils.vector_angle(centerNormal, aroundNormal)>0.5:
            aroundNormal*=-1

        As = self.Data.As[:, orbital]
        layers=['2PX','2PY','2PZ','3PX','3PY','3PZ']
        centerTs=self.Data.get_ts(center,orbital,layers)
        aroundTs=self.Data.get_ts(around,orbital,layers)
        centerTs__=utils.get_projection(centerTs,bondVector,centerNormal)
        aroundTs__=utils.get_projection(aroundTs,bondVector,centerNormal)
        self.logger.info(f'{centerTs__=}\n{aroundTs__=}')
        centerPZs=[each[-1].item() for each in centerTs__]
        aroundPZs=[each[-1].item() for each in aroundTs__]
        self.logger.info(f'{centerPZs=}\n{aroundPZs=}')
        orbitalOrder=sum([cpz*apz/As for cpz,apz in zip(centerPZs,aroundPZs)])*self.orbitalElectron
        self.logger.info(f'{center+1}-{around+1},{orbital+1},{orbitalOrder=}')
        self.orders[f'{center}-{around}-{orbital}']=orbitalOrder
        self.logger.info(f'centerNormal={centerNormal.tolist()}\naroundNormal={aroundNormal.tolist()}')
        return orbitalOrder

    
    def calculate(self,centers): #程序先进行自己的判断与选择
        orbitalNum = self.Data.orbitalNum
        O_orbitals=[orbital for orbital in range(orbitalNum) if self.Data.orbitals[orbital][-1]=='O']
        for center in centers:
            arounds=self.Data.connections(center)
            self.N=len(arounds)
            orderSum=0
            for around in arounds:
                orders=[self.get_orbitalOrder(center,around,orbital) for orbital in O_orbitals]
                sortRes=sorted(zip(O_orbitals,orders),key=lambda s:abs(s[1]),reverse=True)
                orbitals=[each[0] for each in sortRes if abs(each[1])>9e-5]
                orders=[each[1].item() for each in sortRes if abs(each[1])>9e-5]
                orbitalStrs=[f'{orbital+1}' for orbital in orbitals]
                if self.Data.orbitalType==1:
                    orbitalStrs=[(f'α{orbital+1}' if orbital<orbitalNum/2 else f'β{orbital+1-orbitalNum//2}') for orbital in orbitals]
                orderStrs=[f'{each:.4f}' for each in orders]
                self.formatPrint(orbitalStrs,10,8)
                self.formatPrint(orderStrs,10,8)
                bondOrder=np.sum(orders)
                orderSum+=bondOrder
                bondLength=self.Data.bondLength(center,around)
                if bondOrder!=0:
                    self.program.logWindow.insert('end',f'{center+1}-{around+1},BO:{bondOrder:.4f},BL:{bondLength:.4f}\n','BO')
            FV=1.6002-orderSum
            self.program.logWindow.insert('end',f'{center+1},FV:{FV:.4f}\n','FV')

    def formatPrint(self,contents:list[str],number:int,length:int):
        '''
        将列表内容格式化打印
        contents:要打印的内容
        num:每行打印的数量
        len:打印每个元素的长度
        '''
        for i in range(0,len(contents),number):
            string=''.join([each.rjust(length) for each in contents[i:i+number]])
            self.program.logWindow.insert('end',f'{string}\n')
