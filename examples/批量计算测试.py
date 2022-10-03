# 计算扫描文件分割的文件计算单点之后的结果
from pathlib import Path
import sys
import re
import numpy as np
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
print(sys.path)
from pywfn.obj import File
from pywfn.calculators import piBondOrder,overlapIntegrate,piSelectOrder
import os
import matplotlib.pyplot as plt
from hfv import setting
path="E:/BaiduSyncdisk/gFile/C=C/CH2=CH-CH=CH2_Scan"
files=os.listdir(path)
lengths=[]
orders_pi=[]
orders_sigma=[]

with open('examples/mayer键级计算结果.txt','r',encoding='utf-8') as f:
    contents=f.read()

mayer=re.findall(r'#    2:         1\(C \)    3\(C \)    (\d.\d+)', contents)[:-1]
mayer=np.array(mayer,dtype=np.float64)


for i in range(21):
    print(i+1)
    filePath=f'{path}/{i+1}.log'
    file=File(filePath)
    mol=file.mol
    bond=mol.get_bond(1, 3)
    lengths.append(bond.length)
    # 计算键级(π)
    caler=piBondOrder.Calculator(mol)
    res=caler.calculate(bond.a1,bond.a2)
    order=res['data']['order']
    orders_pi.append(order)
    print(order)
    # 计算键级(σ)
    caler=piBondOrder.Calculator(mol,orderType='sigma')
    res=caler.calculate(bond.a1,bond.a2)
    order=res['data']['order']
    orders_sigma.append(order)
    print(order)
    
fig,ax=plt.subplots()
lengths=np.array(lengths)
orders_pi=np.array(orders_pi)
orders_sigma=np.array(orders_sigma)
ax.plot(lengths,orders_pi,label='π',marker='.')
ax.plot(lengths,orders_sigma,label='σ',marker='.')
# ax.plot(lengths,orders_pi+orders_sigma,label='π+σ',marker='.')
ax.plot(lengths,mayer,label='mayer',marker='.')
ax.set_xlabel('bond length')
ax.set_ylabel('bond order')
ax.legend()
# for i,each in enumerate(zip(orders_old,orders_new)):
#     print(each)
plt.show()
