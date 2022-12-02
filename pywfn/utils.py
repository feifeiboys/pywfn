# 将需要的每个模块共同需要的计算都放在这里面
import re
import pandas as pd
import numpy as np
import math
import time
from numba import jit
from . import setting
def get_nums(string):
    res = []
    for each in re.split(r',|，', string):
        content = each.split('-')
        if len(content) == 1:
            res.append(int(each) - 1)
        else:
            res += [int(i) - 1 for i in range(int(content[0]), int(content[1]) + 1)]
    return res


def get_vertical(v1,v2):
    '''获得垂直于两向量的单位向量'''
    v=np.corss(v1,v2)
    return v/np.linalg.norm(v)

def get_points_between_two_pos(pos1,pos2,n):
    '''计算两点之间的点的坐标'''
    dp=pos2-pos1
    all_pos=[pos1+dp/(n-1)*i for i in range(n)]
    return np.array(all_pos)


def coordTrans(nx,ny,nz,coords):
    """对一个向量实行空间坐标变换
    nx,ny,nz: 另一组基坐标
    coord:要尽心变换的坐标/向量
    """
    e=np.array([[1,0,0],[0,1,0],[0,0,1]]).T # 空间坐标变换
    nx,ny,nz=normalize(nx),normalize(ny),normalize(nz)
    e_=np.array([nx,ny,nz]).T
    A_=np.dot(np.linalg.inv(e_),e)
    ps__=np.array([np.dot(A_,p) for p in coords])
    return ps__

arounds=np.array([
        [-1,0,0],
        [+1,0,0],
        [0,-1,0],
        [0,+1,0],
        [0,0,-1],
        [0,0,+1]
    ])
def get_aroundPoints(p,step): # 
    '''
    计算空间中一个点周围六个点处的坐标
    p:[3,]坐标
    step:步长
    '''
    return p+arounds*step


from . import base
def get_extraValue(atom:"base.Atom",obt:int,valueType='max'):
    '''
    从指定位置开始,利用爬山算法寻找原子波函数极值
    maxPos:[3,]
    '''
    p=p0=atom.coord #起始点,p是原子坐标不变
    v0=atom.get_cloud(np.zeros((1,3)),obt) # 计算原子坐标处的初始值
    # print(f'{v0=:.6f},{p0=}')
    step=0.1
    while True:
        aroundPs=get_aroundPoints(p0,step) # aroundPs:(n,3)
        aroundVs=atom.get_cloud(aroundPs-p,obt)
        if valueType=='max' and np.max(aroundVs)>v0:
            # v0=np.max(aroundVs)
            maxID=np.argmax(aroundVs) #最大值的索引
            p0=aroundPs[maxID] # 最大值坐标
            v0=aroundVs[maxID] # 最大值
            # print(f'{v0=:.6f},{p0=}')
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

def differ_function(posan1,posan2): #计算电子分布差值图
    return (posan1+posan2)**2-(posan1**2+posan2**2)/2

@jit(nopython=True)
def get_gridPoints(range,step,ball=False): 
    '''获取空间格点[3,n]'''
    points=[]
    for x in np.arange(-range,range,step):
        for y in np.arange(-range,range,step):
            for z in np.arange(-range,range,step):
                if ball:
                    distance=(x**2+y**2+z**2)**0.5
                    if distance>range:
                        continue
                points.append([x,y,z])
    return np.array(points).T

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

def timeit(func):
    '''定义一个装饰器，统计函数的执行时间'''
    def wrapper(*args,**kwargs):
        start=time.time()
        res=func(*args,**kwargs)
        end=time.time()
        print(f'{func.__name__},{end-start}ms')
        return res
    return wrapper

def k_means(des,points):
    '''定义k-means聚类算法函数,返回每一类对应的索引'''
    N=len(des)
    for epoch in range(5):
        types=[[] for n in range(N)]
        idxs=[[] for n in range(N)]
        for _,each in enumerate(points):
            distance=np.linalg.norm((des-each),axis=1) #计算每个点与中心点的距离(范数)，两个数值
            idx=np.argmin(distance) # 获取距离最近的索引
            types[idx].append(each) # 在索引位置添加点（分类）
            idxs[idx].append(_)
        types=[np.array(each) for each in types]
        pos=np.array([np.mean(each,axis=0) if len(each)>0 else des[i] for i,each in enumerate(types)]) # 获取两个类别的中心点坐标
        des=pos  # 更新目标点
    return idxs

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

def list_remove(l,x):
    new_l=[]
    for each in l:
        if each!=x:
            new_l.append(each)
    return new_l

def connectH(atom,connections):
    '''
    如果连接的有H,就返回C-H键的向量,否则返回None
    '''
    CHVectors=[]
    for each in connections:
        if each['atom_type']=='H':
            CHVectors.append(each['pos']-atom['pos'])
    return CHVectors

def multiple(a,b):
    '''获取两个量之间的倍数关系，必定是大于等于1的'''
    if abs(a)>=abs(b):
        return a/b
    else:
        return b/a

def nodeNum(data):
    '''获取节点曲线中的节点数量，有可能会找多'''
    data[np.where(data==0)]=1e-6
    res=data[:-1]*data[1:]
    return len(np.where(res<=0)[0])

def normalize(vector):
    length=np.linalg.norm(vector)
    if length==0:
        raise
    return vector/length
