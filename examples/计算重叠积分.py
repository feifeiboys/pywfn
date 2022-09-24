"""
重叠积分是两个原子之间的重叠积分，和两个原子的位置以及积分函数类型(由a,l,m,n)有关
"""
import numpy as np
pi=np.pi
e=np.e

mln={
    '1S':[0,0,0]
}
# 轨道系数矩阵
CM=np.array([
    [0.53431,   1.41820],
    [0.53431,  -1.41820]
])
Coords=np.array([ # 每一行是一个原子的坐标
    [0,0,-0.3],
    [0,0, 0.3]
])
layers=['1S','1S']
Bs={
    'H':{
        '1S':{
            'a':[0.3425250914e+01,0.6239137298e+00,0.1688554040e+00],
            'c':[0.1543289673e+00,0.5353281423e+00,0.4446345422e+00]
        }
    }
}

def Si(a,b): # 计算两个GTO之间的积分
    x1,y1,z1,a1,l1,m1,n1=a
    x2,y2,z2,a2,l2,m2,n2=b
    r=(x2-x1)**2+(y2-y1)**2+(z2-z1)**2
    xp=(a1*x1+a2*x2)/(a1+a2)
    yp=(a1*y1+a2*y2)/(a1+a2)
    zp=(a1*z1+a2*z2)/(a1+a2)
    # print(xp,yp,zp)
    S=0
    B=a1+a2
    for i in range((l1+l2)//2+1):
        for j in range((m1+m2)//2+1):
            for k in range((n1+n2)//2+1):
                S+=\
                N(a1,l1,m1,n1)*N(a2,l2,m2,n2)*e**(-a1*a2*r/B)*\
                (x1-xp)**l1*(x2-xp)**l2*(pi/B)**0.5*factorial(2*i-1)/(2*B)**i*\
                (y1-yp)**m1*(y2-yp)**m2*(pi/B)**0.5*factorial(2*j-1)/(2*B)**j*\
                (z1-zp)**n1*(z2-zp)**n2*(pi/B)**0.5*factorial(2*k-1)/(2*B)**k
    # print(S)
    return S

def N(a,l,m,n): #当m,l,n都是0的时候，N是常数
    t=l+m+n
    res=2**(2*t)*a**t/(factorial(2*l-1)*factorial(2*m-1)*factorial(2*n-1))
    res=res*(2/pi)**1.5
    res=res**0.5
    print(res)
    return res

def factorial(num): # 计算二级阶乘
    res=1
    for i in range(1,num+1,2):
        res*=i
    return res

if __name__=='__main__':
    SM=np.zeros(shape=(2,2))
    for i,la1 in enumerate(layers): # 首先对每层进行循环，称之为STO吧，由多个GTO组成
        for j,la2 in enumerate(layers):
            a1s,c1s=Bs['H'][la1]['a'],Bs['H'][la1]['c'] # 获取对应基组对应元素对应基函数的收缩系数和高斯指数
            a2s,c2s=Bs['H'][la2]['a'],Bs['H'][la2]['c']
            s=0
            for a1,c1 in zip(a1s,c1s): # 一个STO元素是9组GTO的乘积
                for a2,c2 in zip(a2s,c2s):
                    l1,m1,n1=mln[la1]
                    l2,m2,n2=mln[la2]
                    x1,y1,z1=Coords[i]
                    x2,y2,z2=Coords[j]
                    a=(x1,y1,z1,a1,m1,l1,n1)
                    b=(x2,y2,z2,a2,m2,l2,n2)
                    print(Si(a, b)*c1*c2)
                    s+=Si(a, b)*c1*c2
            SM[i,j]=s
    print(SM)