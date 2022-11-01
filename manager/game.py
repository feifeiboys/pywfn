"""
制作一个游戏演示点的更新
"""
import time
import numpy as np
import sys


from pywfn.readers import LogReader
from pywfn.data import Elements
elements=Elements()
path=input('输入path:')
reader=LogReader(path)
mol=reader.mol
symbols=[atom.symbol for atom in mol.atoms]

import pygame
from .utils import search,pers
pygame.init()
width=800
height=600
screen = pygame.display.set_mode((width,height))

pygame.display.set_caption('show Mol')
# points=np.random.rand(30,3)*400-200
mx,my,mz=np.abs(mol.coords).max(axis=0)
ml=max(mx,my,mz)
points=(mol.coords/ml)*200
print(points.max(),points.min())
res,steps=search(points)
steps=[e[:3,:].T for e in steps]
steps=[pers(e)*height/2 for e in steps] #为所有的点添加透视效果
bonds=[]

for i in range(len(mol.coords)):
    for j in range(i,len(mol.coords)):
        r=np.linalg.norm(mol.coords[j]-mol.coords[i])
        if 0<r<=1.7:
            bonds.append([i,j])
print(bonds)

def wordPoint(points):
    """将屏幕坐标转为世界坐标,[n,3]"""
    centerPoint=np.array([width/2,height/2,0])
    return points+centerPoint

i=0
d=1
while True:
    # 循环获取事件，监听事件状态
    for event in pygame.event.get():
        # 判断用户是否点了"X"关闭按钮,并执行if代码段
        if event.type == pygame.QUIT:
            #卸载所有模块
            pygame.quit()
            #终止程序，确保退出程序
            sys.exit()
    pygame.draw.rect(screen,'white',(0,0,width,height))
    if i==len(steps)-1:
        d=-1
    if i==0:
        d=1
    i+=d
    wordStep=wordPoint(steps[i])
    for a,(x,y,z) in enumerate(wordStep): # 绘制点
        symbol=symbols[a]
        element=elements.get_element_by_symbol(symbol)
        pygame.draw.circle(screen,element.color, [x,y], 4, width=0)
    for a1,a2 in bonds:
        x1,y1,z1=wordStep[a1]
        x2,y2,z2=wordStep[a2]
        pygame.draw.line(screen, 'black', (x1,y1), (x2,y2), width=1)
    time.sleep(0.1)
    # pygame.display.flip() #更新屏幕内容
    pygame.display.update()
    