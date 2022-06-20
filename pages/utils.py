# 将需要的每个模块共同需要的计算都放在这里面
print('good good study, day day up!!!')
from operator import mul
import matplotlib.pyplot as plt
import re
import pandas as pd
import numpy as np
import sympy
import math
import time
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
    x1,y1,z1=v1
    x2,y2,z2=v2
    sa='(-y1*z2 + y2*z1)*sqrt(1/(x1**2*y2**2 + x1**2*z2**2 - 2*x1*x2*y1*y2 - 2*x1*x2*z1*z2 + x2**2*y1**2 + x2**2*z1**2 + y1**2*z2**2 - 2*y1*y2*z1*z2 + y2**2*z1**2))'
    sb='(x1*z2 - x2*z1)*sqrt(1/(x1**2*y2**2 + x1**2*z2**2 - 2*x1*x2*y1*y2 - 2*x1*x2*z1*z2 + x2**2*y1**2 + x2**2*z1**2 + y1**2*z2**2 - 2*y1*y2*z1*z2 + y2**2*z1**2))'
    sc='-(x1*y2 - x2*y1)*sqrt(1/(x1**2*y2**2 + x1**2*z2**2 - 2*x1*x2*y1*y2 - 2*x1*x2*z1*z2 + x2**2*y1**2 + x2**2*z1**2 + y1**2*z2**2 - 2*y1*y2*z1*z2 + y2**2*z1**2))'
    a=sympy.sympify(sa).subs([('x1',x1),('y1',y1),('z1',z1),('x2',x2),('y2',y2),('z2',z2)])
    b=sympy.sympify(sb).subs([('x1',x1),('y1',y1),('z1',z1),('x2',x2),('y2',y2),('z2',z2)])
    c=sympy.sympify(sc).subs([('x1',x1),('y1',y1),('z1',z1),('x2',x2),('y2',y2),('z2',z2)])
    return np.array([float(a),float(b),float(c)])

def get_points_between_two_pos(pos1,pos2,n):
    '''计算两点之间的点的坐标'''
    dp=pos2-pos1
    all_pos=[pos1+dp/(n-1)*i for i in range(n)]
    return np.array(all_pos)
def posan_function(centerPos,aroundPos,paras,ts,onlyP=False): # 为了代码可读性，可以适当写出来罗嗦点的代码
    '''计算中心原子周围点处的函数值'''
    alphas=paras[:,0]
    c_s=paras[:,1]
    c_p=paras[:,2]
    x,y,z=aroundPos.reshape(3,-1)
    x0,y0,z0=centerPos.reshape(3,-1)
    R=np.sum((centerPos-aroundPos)**2,axis=0,keepdims=True)
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
    ps=[s2,px2,py2,pz2,s3,px3,py3,pz3]
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
        ts=get_coefficients('2SP',Data.atoms,atom,orbital,raw=True)
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
        aroundValues=posan_function(atomPos,aroundPos,paras,ts)
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
def get_gridPoints(range,step,ball=False): 
    '''获取空间格点'''
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
    if value>1:
        value=1
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

def get_slope(data,step,n):
    return np.diff(data,n)/step**n

def get_changeScope(slope):
    return np.sum((slope-slope.mean())**2)

def get_sCoefficients(stype,atoms,atom,orbitals,raw=False):
    '''获得1S,2S,3S的归一化后的系数'''
    if stype=='1S':
        res=atoms[atom]['datas'].loc[['1S'],:].iloc[:,orbitals]
    elif stype=='2S':
        res=atoms[atom]['datas'].loc[['2S','3S'],:].iloc[:,orbitals]
    if raw: #是否返回原始数据
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)
def get_pCoefficients(atoms,atom,orbitals,raw=False):
    '''获得2S,3S,2PX,2PY,2PZ,3PX,3PY,3PZ的归一化后的系数'''
    
    res=atoms[atom]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,orbitals]
    
    if raw: #是否返回原始数据
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)
def get_2spCoefficients(atoms,atom,orbitals,raw=False):
    res=atoms[atom]['datas'].loc[['2S','2PX','2PY','2PZ','3S','3PX','3PY','3PZ'],:].iloc[:,orbitals]
    
    if raw: #是否返回原始数据
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)

def get_dCoefficients(atoms,atom,orbitals,raw=False):
    
    hasD=False if sum([1 if each in atoms[atom]['datas'].index else 0 for each in ['4XX','4YY','4ZZ','4XY','4XZ','4YZ']])==0 else True
    if hasD:
        res=atoms[atom]['datas'].loc[['4XX','4YY','4ZZ','4XY','4XZ','4YZ'],:].iloc[:,orbitals]
    else:
        res=np.zeros(shape=(6,len(orbitals) if isinstance(orbitals,list) else 1))
    if raw:
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)
    

def get_coefficients(type,atoms,atom,orbitals,raw=False):
    if type=='1S':
        return get_sCoefficients('1S',atoms,atom,orbitals,raw)
    elif type=='2S':
        return get_sCoefficients('2S',atoms,atom,orbitals,raw)
    elif type=='SP':
        return get_sCoefficients('2S',atoms,atom,orbitals,raw)+get_pCoefficients(atoms,atom,orbitals,raw)
    elif type=='2SP':
        return get_2spCoefficients(atoms,atom,orbitals,raw)
    elif type=='P':
        return get_pCoefficients(atoms,atom,orbitals,raw)
    elif type=='D':
        return get_dCoefficients(atoms,atom,orbitals,raw)
    elif type=='SD':
        return get_sCoefficients('1S',atoms,atom,orbitals,raw)+get_dCoefficients(atoms,atom,orbitals,raw)

def get_allSCoefficients(atoms,orbital,all_square_sum):
    all_sCoefficients=np.array([])
    for atom in atoms:
        hasS=False if sum([1 if each in atom['datas'].index else 0 for each in ['1S']])==0 else True
        if hasS:
            eachCofficients=atom['datas'].loc[['1S'],:].iloc[:,orbital]
            eachCofficients=np.sum(eachCofficients.to_numpy()**2,axis=0)/all_square_sum[:,orbital]
        else:
            eachCofficients=0
        all_sCoefficients=np.append(all_sCoefficients,eachCofficients)
    return all_sCoefficients.sum()

def get_allDCoefficients(atoms,orbital,all_square_sum):
    all_sCoefficients=np.array([])
    for atom in atoms:
        hasD=False if sum([1 if each in atom['datas'].index else 0 for each in ['4XX','4YY','4ZZ','4XY','4XZ','4YZ']])==0 else True
        if hasD:
            eachCofficients=atom['datas'].loc[['4XX','4YY','4ZZ','4XY','4XZ','4YZ'],:].iloc[:,orbital]
            eachCofficients=np.sum(eachCofficients.to_numpy()**2,axis=0)/all_square_sum[:,orbital]
        else:
            eachCofficients=0
        all_sCoefficients=np.append(all_sCoefficients,eachCofficients)
    return all_sCoefficients.sum()

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