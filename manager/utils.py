"""
数学运算
"""
import numpy as np
import hashlib
import random
# 坐标变化
def T(x,y,z):
    """生成平移矩阵"""
    return np.array([
        [1,0,0,x],
        [0,1,0,y],
        [0,0,1,z],
        [0,0,0,1]
    ])

def S(x,y,z):
    """生层缩放矩阵"""
    return np.array([
        [x,0,0,0],
        [0,y,0,0],
        [0,0,z,0],
        [0,0,0,1]
    ])

def R(w,a):
    """旋转方向和旋转角度"""
    s=np.sin(a)
    c=np.cos(a)
    if w=='x':
        m=np.array([
            [1,0,0,0],
            [0,c,-s,0],
            [0,s,c,0],
            [0,0,0,1]
        ])
        return m
    elif w=='y':
        m=np.array([
            [c,0,s,0],
            [0,1,0,0],
            [-s,0,c,0],
            [0,0,0,1]
        ])
        return m
    elif w=='z':
        m=np.array([
            [c,-s,0,0],
            [s,c,0,0],
            [0,0,1,0],
            [0,0,0,1]
        ])
        return m
    else:
        raise

def get_area(points):
    """计算x,y两个维度的面积,[4,n]"""
    x1,y1=np.min(points[:2,:],axis=1)
    x2,y2=np.max(points[:2,:],axis=1)
    return (x2-x1)*(y2-y1)

def get_arounds(points):
    
    """返回该构象周围的六个构象,points:[4,n]"""
    da=0.1
    arounds=[
        R('x',da)@points,
        R('x',-da)@points,
        R('y',da)@points,
        R('y',-da)@points,
        # R('z',da)@points,
        # R('z',-da)@points,
    ]
    random.shuffle(arounds)
    return arounds

def search(points):
    """爬山法搜索时显示面积最大的旋转结果,points:[n,3]->[n,3]"""
    points=points.T #[3,n]
    _,n=points.shape
    points=np.concatenate([points,np.ones(shape=(1,n))]) #[4,n]
    area=get_area(points)
    print(f'{area=}')
    steps=[points]
    while True:
        arounds=get_arounds(points) # 获取该点周围的构象
        areas=[get_area(e) for e in arounds]
        print(areas)
        for each in areas:
            if each>area:
                maxArea=each
            else:
                maxArea=max(areas)
        if maxArea>area:
            maxIdx=areas.index(maxArea)
            area=areas[maxIdx]
            points=arounds[maxIdx]
            steps.append(points)
            print(f'{area=}')
        else:
            return points[:3,:].T,steps
        
def pers(p):
    """
    获得3d坐标的透视坐标,p[n,3]
    摄像机在z轴的-2处,所有的点缩放范围在(-1,1)之间
    """
    n,_=p.shape
    mx,my,mz=np.abs(p).max(axis=0)
    p=p/max([mx,my,mz])
    o=np.array([0,0,-2]).reshape(1,3)
    z_=np.array([0,0,-1.5]).reshape(1,3)
    z=p.copy()[:,-1].reshape(n,1)
    oz=z-o
    oz_=z_-o
    op=p-o
    op_=op*(oz_[:,-1]/oz[:,-1]).reshape(n,1)
    p_=o+op_
    p_[:,-1]=0
    p_*=2
    return p_

def get_fileHash(path):
        """为了避免导入文件重复,计算文件哈希值"""
        m=hashlib.md5()
        with open(path,'rb') as f:
            while True:
                data=f.read(1024)
                if not data:
                    break
                m.update(data)
        return m.hexdigest()

def get_randomName():
    """获取一个随机名称"""
    s='1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    res=random.choices(s,k=20)
    return ''.join(res)

if __name__=='__main__':
    points=np.random.rand(5,3)*2
    res,steps=search(points)