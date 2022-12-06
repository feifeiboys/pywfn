"""
基组数据是必须的，从高斯文件中读取可以，但是fch文件中并不含有基组数据，因此提前保存好常用的基组数据
"""

from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import numpy as np

from pywfn.readers import FchReader,LogReader
from pywfn.bondorder import piDM
import json
import basis_set_exchange as bse
from tqdm import tqdm

famis=["pople","ahlrichs","lanl","dunning"]
famis=["pople"]

allBaseData={}
for each in bse.get_all_basis_names():

    
    base=bse.get_basis(each)
    if bse.get_basis_family(each) not in famis:continue
    elements=base['elements']
    name=base['name']
    baseData={}
    print(name,len(elements))
    for element in elements:
        # print(element)
        baseData[element]=[]
        
        shells=elements[element]['electron_shells']
        for shell in shells:
            ang=shell['angular_momentum']
            exp=shell['exponents']
            coe=shell['coefficients']
            exp=[float(e) for e in exp]
            coe=[[float(e) for e in line] for line in coe]

            baseData[element].append({
                'ang':ang,
                'exp':exp,
                'coe':coe
            })
    allBaseData[name]=baseData
with open(f'pywfn/data/basis.json','w',encoding='utf-8') as f:
    f.write(json.dumps(allBaseData))
# res=bse.get_basis('6-31g*')
# with open('basi.json','w',encoding='utf-8') as f:
#     f.write(json.dumps(res))