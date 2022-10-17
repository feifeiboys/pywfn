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

def get_projection(ts,x_,z_):
    '''计算原子轨道组合系数在法向量的投影,x_是键轴方向,z_是法向量或者轨道方向'''
    if np.linalg.norm(x_)==0 or np.linalg.norm(z_)==0:
        raise
    x_=x_/np.linalg.norm(x_)
    z_=z_/np.linalg.norm(z_)
    y_=np.cross(x_,z_)
    if np.linalg.norm(y_)==0:
        raise
    y_=y_/np.linalg.norm(y_)
    ps=[np.array(ts[i:i+3]) for i in range(0,len(ts),3)] #每一项都是长度为3的数组
    ps_=[np.dot(p, z_)/np.linalg.norm(z_)*z_ for p in ps] # 轨道向量在法向量方向上的投影

    e=np.array([[1,0,0],[0,1,0],[0,0,1]]).T # 空间坐标变换
    e_=np.array([x_,y_,z_]).T
    A_=np.dot(np.linalg.inv(e_),e)
    ps__=np.array([np.dot(A_,p[:,np.newaxis]) for p in ps_])
    return ps__

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

def posan_function(centerPos,aroundPos,paras,ts,onlyP=False): # 为了代码可读性，可以适当写出来罗嗦点的代码
    '''计算中心原子周围点处的函数值'''
    alphas=paras[:,0]
    c_s=paras[:,1]
    c_p=paras[:,2]
    x,y,z=aroundPos.reshape(3,-1)
    x0,y0,z0=centerPos.reshape(3,-1)
    R=np.sum((aroundPos-centerPos)**2,axis=0,keepdims=True)
    psx=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(x-x0)*math.e**(-1*a*R)
    psy=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(y-y0)*math.e**(-1*a*R)
    psz=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(z-z0)*math.e**(-1*a*R)
    s=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*math.e**(-1*a*R)
    px2=sum([c*psx(a) for c,a in zip(c_p[:-1],alphas[:-1])])  # 对于3-21
    py2=sum([c*psy(a) for c,a in zip(c_p[:-1],alphas[:-1])])
    pz2=sum([c*psz(a) for c,a in zip(c_p[:-1],alphas[:-1])])
    px3=c_p[-1]*psx(alphas[-1])
    py3=c_p[-1]*psy(alphas[-1])
    pz3=c_p[-1]*psz(alphas[-1])
    s2=sum([c*s(a) for c,a in zip(c_s[:-1],alphas[:-1])])
    s3=c_p[-1]*s(alphas[-1])
    if onlyP:
        s2=s3=0
    s2=s3=0
    ps=[px2,py2,pz2,px3,py3,pz3]
    mo=sum([t*p for t,p in zip(ts,ps)])
    return mo
def multiFunction(orbital:int,atoms:list,selectPos,Data):
    '''
    计算多个原子的波函数在指定点的叠加
    atoms:多个原子的序数
    aroundPos:指定的点
    '''
    res=[]
    for atom in atoms:
        atomPos=Data.atomPos(atom).reshape(3,1)
        paras = np.array(Data.standard_basis[atom])
        layers=['2PX','2PY','2PZ','3PX','3PY','3PZ']
        ts=Data.get_ts(atom,orbital,layers)
        values=posan_function(atomPos,selectPos,paras,ts)
        res.append(values)
    return np.array(res).sum(axis=0).flatten()

def get_aroundPoints(p,step): # 
    '''
    计算空间中一个点周围六个点处的坐标
    p:(3,1)坐标
    step:步长
    '''
    x,y,z=p.flatten()
    return np.array([
        [x-step,y,z],
        [x+step,y,z],
        [x,y-step,z],
        [x,y+step,z],
        [x,y,z-step],
        [x,y,z+step]
    ]).T
def removePos(aroundPos,searched):
    '''去除已经搜索过的点'''
    idxs=[]
    for i,each in enumerate(aroundPos.T):
        x,y,z=each
        key=f'{x:.6f}-{y:.6f}-{z:.6f}'
        if key not in searched:
            idxs.append(i)
    return aroundPos[:,idxs]
def addSearched(aroundPos,searched):
    '''将已经搜索过的添加到搜索中'''
    for i,each in enumerate(aroundPos.T):
        x,y,z=each
        key=f'{x:.6f}-{y:.6f}-{z:.6f}'
        searched.append(key)
    return searched
def get_extraValue(atomPos,paras,ts,valueType):
    '''
    从指定位置开始,利用爬山算法寻找函数极值
    atomPos:(3,1)
    maxPos:(3,1)
    '''
    startPos=atomPos.copy()
    startValue=0 # 计算原子坐标处的初始值
    step=0.1
    while True:
        aroundPos=get_aroundPoints(startPos,step) # aroundPos:(3,n)
        aroundValues=posan_function(atomPos,aroundPos,paras,ts,onlyP=True)
        if valueType=='max' and np.max(aroundValues)>startValue:
            startValue=np.max(aroundValues)
            maxID=np.argmax(aroundValues)
            startPos=aroundPos[:,maxID].reshape(3,1)
        elif valueType=='min' and np.min(aroundValues)<startValue:
            startValue=np.min(aroundValues)
            minID=np.argmin(aroundValues)
            startPos=aroundPos[:,minID].reshape(3,1)
        else:
            if step<=1e-6:
                return startPos,startValue # startPos:(3,1)
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
    '''获取三点确定的平面的单位法向量'''
    x1,y1,z1=p1
    x2,y2,z2=p2
    x3,y3,z3=p3
    A = (y2 - y1)*(z3 - z1) - (z2 - z1)*(y3 - y1)
    B = (z2 - z1)*(x3 - x1) - (x2 - x1)*(z3 - z1)
    C = (x2 - x1)*(y3 - y1) - (y2 - y1)*(x3 - x1)
    n=np.array([A,B,C])
    return n/np.linalg.norm(n) # 返回单位向量

def get_dihedralAngle(p1,p2,p3,p4):
    '''根据四个点，计算二面角'''
    n1=get_normalVector(p1,p2,p3)
    n2=get_normalVector(p4,p3,p2)
    return vector_angle(n1,n2)

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
def orbital_classify(atom,vectors,O_orbitals):
    '''定义函数将轨道分类'''
    points=[]
    orbitals=[]
    keys=vectors.keys()
    for key in keys:
        atomidx=int(key.split('-')[0])
        orbitalidx=int(key.split('-')[1])
        if atomidx==atom and orbitalidx in O_orbitals and vectors[key] is not None:
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

class Printer:
    def __init__(self) -> None:
        self.debug=setting.DEBUG
    def __call__(self, content):
        if self.debug:
            print(f'debug:{content}')
