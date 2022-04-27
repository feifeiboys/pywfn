# 将需要的每个模块共同需要的计算都放在这里面
print('this is utils')
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
def posan_function(centerPos,aroundPos,alphas,cs,ts): # 为了代码可读性，可以适当写出来罗嗦点的代码
    '''计算中心原子周围点处的函数值'''
    x,y,z=aroundPos.reshape(3,-1)
    x0,y0,z0=centerPos.reshape(3,-1)
    R=np.sum((centerPos-aroundPos)**2,axis=0,keepdims=True)
    psx=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(x-x0)*math.e**(-1*a*R)
    psy=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(y-y0)*math.e**(-1*a*R)
    psz=lambda a:(2*a/math.pi)**(3/4)*2*a**0.5*(z-z0)*math.e**(-1*a*R)
    px2=sum([c*psx(a) for c,a in zip(cs[:-1],alphas[:-1])])  # 对于3-21
    py2=sum([c*psy(a) for c,a in zip(cs[:-1],alphas[:-1])])
    pz2=sum([c*psz(a) for c,a in zip(cs[:-1],alphas[:-1])])
    px3=cs[-1]*psx(alphas[-1])
    py3=cs[-1]*psy(alphas[-1])
    pz3=cs[-1]*psz(alphas[-1])
    ps=[px2,py2,pz2,px3,py3,pz3]
    mo=sum([t*p for t,p in zip(ts,ps)])
    return mo

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

def vector_angle(a,b): # 计算两向量之间的夹角
    '''计算两向量之间的夹角'''
    value=(np.dot(a,b))/(np.linalg.norm(a)*np.linalg.norm(b))
    if value>1:
        value=1
    return np.arccos(value)/math.pi

def get_normalVector(p1,p2,p3):
    '''获取三点确定的平面的单位法向量'''
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
    return n # 返回单位向量

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
def obtial_classify(atom,vectors,O_obtials):
    '''定义函数将轨道分类'''
    points=[]
    obtials=[]
    keys=vectors.keys()
    for key in keys:
        atomidx=int(key.split('-')[0])
        obtialidx=int(key.split('-')[1])
        if atomidx==atom and obtialidx in O_obtials and vectors[key] is not None:
            vector=vectors[key]/np.linalg.norm(vectors[key])
            points.append(vector)
            obtials.append(obtialidx)
    if len(points)>0:
        points=np.array(points)
        idxs=linear_classify(points)
    else:
        idxs=[[],[]]
    V,H=[[obtials[id] for id in idx] for idx in idxs]
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

def get_sCoefficients(stype,atoms,atom,obtials,raw=False):
    '''获得1S,2S,3S的归一化后的系数'''
    if stype=='1S':
        res=atoms[atom]['datas'].loc[['1S'],:].iloc[:,obtials]
    elif stype=='2S':
        res=atoms[atom]['datas'].loc[['2S','3S'],:].iloc[:,obtials]
    if raw: #是否返回原始数据
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)
def get_pCoefficients(atoms,atom,obtials,raw=False):
    '''获得2S,3S,2PX,2PY,2PZ,3PX,3PY,3PZ的归一化后的系数'''
    
    res=atoms[atom]['datas'].loc[['2PX','2PY','2PZ','3PX','3PY','3PZ'],:].iloc[:,obtials]
    
    if raw: #是否返回原始数据
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)

def get_dCoefficients(atoms,atom,obtials,raw=False):
    
    hasD=False if sum([1 if each in atoms[atom]['datas'].index else 0 for each in ['4XX','4YY','4ZZ','4XY','4XZ','4YZ']])==0 else True
    if hasD:
        res=atoms[atom]['datas'].loc[['4XX','4YY','4ZZ','4XY','4XZ','4YZ'],:].iloc[:,obtials]
    else:
        res=np.zeros(shape=(6,len(obtials) if isinstance(obtials,list) else 1))
    if raw:
        return res
    else:
        return np.sum(res.to_numpy()**2,axis=0)
    

def get_coefficients(type,atoms,atom,obtials,raw=False):
    if type=='1S':
        return get_sCoefficients('1S',atoms,atom,obtials,raw)
    elif type=='2S':
        return get_sCoefficients('2S',atoms,atom,obtials,raw)
    elif type=='SP':
        return get_sCoefficients('2S',atoms,atom,obtials,raw)+get_pCoefficients(atoms,atom,obtials,raw)
    elif type=='P':
        return get_pCoefficients(atoms,atom,obtials,raw)
    elif type=='D':
        return get_dCoefficients(atoms,atom,obtials,raw)
    elif type=='SD':
        return get_sCoefficients('1S',atoms,atom,obtials,raw)+get_dCoefficients(atoms,atom,obtials,raw)

def get_allSCoefficients(atoms,obtial,all_square_sum):
    all_sCoefficients=np.array([])
    for atom in atoms:
        hasS=False if sum([1 if each in atom['datas'].index else 0 for each in ['1S']])==0 else True
        if hasS:
            eachCofficients=atom['datas'].loc[['1S'],:].iloc[:,obtial]
            eachCofficients=np.sum(eachCofficients.to_numpy()**2,axis=0)/all_square_sum[:,obtial]
        else:
            eachCofficients=0
        all_sCoefficients=np.append(all_sCoefficients,eachCofficients)
    return all_sCoefficients.sum()

def get_allDCoefficients(atoms,obtial,all_square_sum):
    all_sCoefficients=np.array([])
    for atom in atoms:
        hasD=False if sum([1 if each in atom['datas'].index else 0 for each in ['4XX','4YY','4ZZ','4XY','4XZ','4YZ']])==0 else True
        if hasD:
            eachCofficients=atom['datas'].loc[['4XX','4YY','4ZZ','4XY','4XZ','4YZ'],:].iloc[:,obtial]
            eachCofficients=np.sum(eachCofficients.to_numpy()**2,axis=0)/all_square_sum[:,obtial]
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