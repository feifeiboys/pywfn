import numpy as np
from typing import *
from .gto import Gto
import math
from .. import setting

def gridPos(range):
    """生成网格数据点,range:生成数据的范围"""
    ...

def CM2PM(CM,orbital:List[int],oe:int):
    """
    根据系数矩阵构建密度矩阵
    CM:系数矩阵,如果是开壳层的话,列数是行数的两倍[n,n]/[n,2n]
    n:分子轨道占据电子数
    """
    PMs=CM2PMs(CM,orbital,oe)
    return np.sum(PMs,axis=0)

def CM2PMs(CM,orbital:List[int],oe:int):
    """
    构建三维密度矩阵，不要空轨道，形状为[占据轨道数,原子轨道数,原子轨道数]
    """
    A=(CM[:,orbital].T)[:,:,np.newaxis]
    B=(CM[:,orbital].T)[:,np.newaxis,:]
    return A@B*oe #用矩阵乘法的形式直接构建矩阵可比逐元素计算多了

def vector_angle(a,b,trans=False): # 计算两向量之间的夹角
    '''计算两向量之间的夹角'''
    if np.linalg.norm(a)*np.linalg.norm(b)==0:
        raise
    value=np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
    if value>1:value=1
    if value<-1:value=-1
    angle=np.arccos(value)/math.pi
    if not trans:
        return angle
    else:
        return 0.5-abs(angle-0.5)
    
def get_normalVector(p1,p2,p3):
    '''
    获取三点确定的平面的单位法向量
    根据两个向量也可以确定法向量
    '''
    vi=p3-p2
    vj=p1-p2
    n=np.cross(vi,vj)
    if vector_angle(n,setting.BASE_VECTOR)>0.5:n*=-1
    return n/np.linalg.norm(n) # 返回单位向量

def linear_classify(points): #将向量分类转为表示角度的数值分类
    nv=points[-1]
    angles=np.array([vector_angle(each,nv) for each in points])
    y=np.abs(0.5-angles)
    types=[[],[]]
    idxs=[[],[]]
    for i,each in enumerate(y):
        distance=np.abs(each-np.array([0,0.5]))
        idx=np.argmin(distance)
        types[idx].append(each)
        idxs[idx].append(i)
    return idxs

def orbital_classify(atom,vectors,O_obts):
    '''定义函数将轨道分类'''
    points=[]
    orbitals=[]
    keys=vectors.keys()
    for key in keys:
        atomidx=int(key.split('-')[0])
        orbitalidx=int(key.split('-')[1])
        if atomidx==atom and orbitalidx in O_obts and vectors[key] is not None:
            vector=vectors[key]/np.linalg.norm(vectors[key])
            points.append(vector)
            orbitals.append(orbitalidx)
    if len(points)>0:
        points=np.array(points)
        idxs=linear_classify(points)
    else:
        idxs=[[],[]]
    V,H=[[orbitals[id] for id in idx] for idx in idxs]
    return V,H

def get_aroundPoints(p,step): # 
    '''
    计算空间中一个点周围六个点处的坐标
    p:[3,]坐标
    step:步长
    '''
    arounds=np.array([
        [-1,0,0],
        [+1,0,0],
        [0,-1,0],
        [0,+1,0],
        [0,0,-1],
        [0,0,+1]
    ])
    return p+arounds*step

from .. import base
def get_extraValue(atom:"base.Atom",obt:int,valueType='max'):
    '''
    从指定位置开始,利用爬山算法寻找原子波函数极值
    maxPos:[3,]
    '''
    # p0=atom.coord.copy() # 起始点,p是原子坐标不变
    # p=p0.copy()
    p0=np.array([0.,0.,0.]).reshape(1,3)
    v0=atom.get_cloud(p0,obt) # 计算原子坐标处的初始值
    # print(f'{v0=:.6f},{p0=}')
    step=0.1
    while True:
        aroundPs=get_aroundPoints(p0,step) # aroundPs:(n,3)
        aroundVs=atom.get_cloud(aroundPs,obt)
        if valueType=='max' and np.max(aroundVs)>v0:
            maxID=np.argmax(aroundVs) #最大值的索引
            p0=aroundPs[maxID] # 最大值坐标
            v0=aroundVs[maxID] # 最大值
        elif valueType=='min' and np.min(aroundVs)<v0:
            # v0=np.min(aroundVs)
            minID=np.argmin(aroundVs)
            p0=aroundPs[minID]
            v0=aroundVs[minID]
        else:
            if step<=1e-6:
                return p0,v0 #
            else:
                step/=10