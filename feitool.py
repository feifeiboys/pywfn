# 此脚本记录在工作中常用的函数
import numpy as np
from numpy import sin,cos
import pandas as pd
import pyautogui
import os
import time
import re
def rotateX(vectors,angle):
    line,colum=vectors.shape
    vectors=np.concatenate([vectors,np.ones(shape=(1,colum))],axis=0)

    matrix=np.array([
        [cos(angle),-sin(angle),0,0],
        [sin(angle), cos(angle),0,0],
        [0            ,0,             1,0],
        [0            ,0,             0,0],
    ])
    return np.dot(matrix,vectors).T[:,:-1]
def rotateY(vectors,angle):
    line,colum=vectors.shape
    vectors=np.concatenate([vectors,np.ones(shape=(1,colum))],axis=0)

    matrix=np.array([
        [cos(angle),0,-sin(angle),0],
        [0,1,0,0],
        [sin(angle),0,cos(angle),0],
        [0,0,0,1],
    ])
    return np.dot(matrix,vectors).T[:,:-1]
def rotateZ(vectors,angle):
    line,colum=vectors.shape
    vectors=np.concatenate([vectors,np.ones(shape=(1,colum))],axis=0)

    matrix=np.array([
        [1,0,0,0],
        [0,cos(angle),-sin(angle),0],
        [0,sin(angle),cos(angle),0],
        [0,0,0,1],
    ])
    return np.dot(matrix,vectors).T[:,:-1]
def readGjf(path):
    with open(path,'r',encoding='utf-8') as f:
        content=f.read()
    res=re.findall(r'([A-Za-z]+) +(-?\d+.\d{8}) +(-?\d+.\d{8}) +(-?\d+.\d{8})',content)
    print(res)
    res=pd.DataFrame(res)

    atoms=res.iloc[:,0]
    cords=res.iloc[:,1:]
    return atoms,cords.to_numpy(dtype=np.float32)

def array2Str(array,atoms):
    lines=[]
    for i,each in enumerate(array):
        line=f'{atoms[i]}'.rjust(2,' ')+' '*17+''.join([f'{p:.8f}'.rjust(14,' ') for p in each.tolist()])
        lines.append(line)
    return '\n'.join(lines)
def createRotateFile():
    '''创建某些基团旋转后的文件'''
    atoms,cords=readGjf(r"C:\code\HFV\files\lianben\lianben.gjf")
    group=[0,1,2,3,4,5,12,13,14,15,16]
    with open(r"C:\code\HFV\files\lianben\template.txt",'r',encoding='utf-8') as f:
        template=f.read()
    for i in range(37):
        cordsCopy=cords.copy()
        cordsCopy[group,:]=rotateZ(cordsCopy[group,:].T,i*np.pi/36)
        resStr=array2Str(cordsCopy,atoms)
        with open(r"C:\code\HFV\files\lianben\files\lianbenScan_"+f'{i}.gjf','w',encoding='utf-8') as f:
            f.write(template.replace('COORDINATE',resStr).replace('IDX',f'{i}'))

def gaussianRun():
    '''运行高斯批量处理输入文件'''
    for i in range(37):
        print('g16 '+r'C:\code\HFV\files\lianbenR\files\lianBenScanRHF_'+f'{i}'+r' C:\code\HFV\files\lianbenR\files\lianBenScanRHF_'+f'{i}')

def formchk():
    '''chk转fch'''
    formchkPath=r"C:\programs\g16w\formchk.exe"
    for i in range(37):
        # "C:\code\HFV\files\scan\files\DINGERXISCAN_1.chk"
        os.system(formchkPath+r' C:\code\HFV\files\lianbenR\files\lianBenScanR_'+f'{i}'+'.chk')

def autoMultiwfn():
    '''自动操作multiwfn生成mayer健级'''
    for i in range(5):
        print(f'\r{5-i}/5',end='')
        time.sleep(1)
    for i in range(37):
        pyautogui.typewrite(r'C:\code\HFV\files\lianbenR\files\lianBenScanR_'+f'{i}.fch')
        pyautogui.press(['enter','9','enter','1','enter','n','enter','0','enter','r','enter'],interval=1.0)

def auto_gjf():
    '''根据模板生成gif'''
    pass

def splitScan():
    '''将扫描的文件中每一个结构拆分'''
    with open(r"C:\code\HFV\files\lianbenR\lianbenScan.out",'r',encoding='utf-8') as f:
        data=f.read()
    with open(r"C:\code\HFV\files\lianbenR\template.txt",'r',encoding='utf-8') as f:
        template=f.read()
    contents=data.split(' Optimization completed.')
    atoms='C'*12+'H'*10
    for idx,content in enumerate(contents):
        lines=content.split('\n')
        lineNum=0
        for i,line in enumerate(lines):
            if 'Input orientation:' in line:
                lineNum=i
        print(lineNum)
        posStr='\n'.join(lines[lineNum+4:lineNum+28])
        # print(posStr)
        res=re.findall(r'-?\d.\d{6} +-?\d.\d{6} +-?\d.\d{6}',posStr)
        res='\n'.join([f'{atoms[j]} {each}' for j,each in enumerate(res)])
        # print(res)
        writeContent=template.replace('IDX',f'{idx}').replace('COORDINATE',res)
        with open(r"C:\code\HFV\files\lianbenR\files\lianBenScanRHF_"+f'{idx}.gjf','w',encoding='utf-8') as f:
            f.write(writeContent)

if __name__=='__main__':
    gaussianRun()
