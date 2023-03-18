"""
存储一些与显示图形相关的函数，为了与utils区分命名为util
"""
import numpy as np

def inArray(elements,array): #一个一维向量是否在二位向量中
    '''
    判断一些向量是否在另一些向量中
    '''
    elements=elements[:,0]*1e12+elements[:,1]*1e8+elements[:,2]*1e4
    array=array[:,0]*1e12+array[:,1]*1e8+array[:,2]*1e4
    res=np.isin(elements,array)
    return res

def get_borders(gridData):
    '''
    获得点云边界点的坐标
    '''
    point=np.round(gridData.copy(),decimals=1)
    gridData=np.round(gridData.copy(),decimals=1)

    arounds=np.array([ #定义六个方向
        [-0.1,0,0],
        [0.1,0,0],
        [0,-0.1,0],
        [0,0.1,0],
        [0,0,-0.1],
        [0,0,0.1]
    ])
    res=np.zeros(point.shape[0])
    for i in range(6):
        around=arounds[i].reshape(1,3)
        aroundPos=np.round(point+around,decimals=1)
        res+=inArray(elements=aroundPos,array=gridData)
    indexs=np.where(res!=6)[0]
    return gridData[indexs,:]

def splited(data): #将数据点分为正负两部分
        positiveValues=[]
        negativeValues=[]
        for each in data:
            if each[-1]>0:
                positiveValues.append(each)
            elif each[-1]<0:
                negativeValues.append(each)
        return np.array(positiveValues),np.array(negativeValues)
        
def limited(values,limit,limitType='more'): # 挑选出大于指定值的函数值
    # limit=app.setting['functionValueLimit']
    limitValues=[]
    if limitType=='more':
        for each in values:
            if abs(each[-1])>limit:
                limitValues.append(each)
    elif limitType=='less':
        for each in values:
            if abs(each[-1])<limit:
                limitValues.append(each)
    return np.array(limitValues)

def hex2rgb(hexcolor:str):
    '''HEX转RGB'''
    hexcolor=hexcolor.replace('#', '')
    hexcolor = int(hexcolor, base=16)
    rgb = (hexcolor >> 16) & 0xff , (hexcolor >> 8) & 0xff , hexcolor & 0xff 
    return rgb[0]/255,rgb[1]/255,rgb[2]/255

def rgb(r,g,b):
    return r/255,g/255,b/255