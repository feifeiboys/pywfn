"""
根据三维点绘制图像
"""
from pywfn.data import Elements
from pywfn.base import Mol
elements=Elements()
from PIL import Image,ImageDraw
from . import utils
from pywfn.readers import LogReader
from pywfn.base import Mol
import numpy as np

imgSize=400
atomRadius=int(imgSize/100)
bondWidth=int(atomRadius/5)
def saveImg(mol:Mol,path):
    """传入2d点绘制分子"""
    
    coords=mol.coords
    bonds=[]
    for i in range(len(coords)):
        for j in range(i,len(coords)):
            if 0<np.linalg.norm(coords[j]-coords[i])<1.7:
                bonds.append([i,j])
    symbols=[atom.symbol for atom in mol.atoms()]

    points=deduction(coords)*imgSize+imgSize/2

    img=Image.new('RGB',(imgSize,imgSize),color='white')
    draw=ImageDraw.Draw(img)
    d=atomRadius
    for i,(x,y) in enumerate(points):# 绘制原子
        symbol=symbols[i]
        color=elements.get_element_by_symbol(symbol).color
        draw.ellipse((x-d, y-d, x+d, y+d), fill=color, width=0) 

    for a1,a2 in bonds:
        x1,y1=points[a1]
        x2,y2=points[a2]
        draw.line([(x1,y1),(x2,y2)],fill='black',width=bondWidth,joint=None)
    img.save(path)

def deduction(coords):
    """返回投影到2d屏幕的坐标,[n,2],范围在-1,1之间"""
    points,steps=utils.search(coords) # 寻找最优的旋转结构
    points=utils.pers(points) # 计算透视坐标
    return points[:,:-1]