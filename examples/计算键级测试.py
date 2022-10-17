from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pywfn.readers import LogReader
from pywfn.calculators import piBondOrder,piSelectOrder,mayerBondOrder
orders1=[]
orders2=[]
orders3=[]
lengths=[]
a1,a2=[3,12]
for i in range(37):
    
    mol=LogReader(fr"D:\BaiduSyncdisk\gFile\scans\lianben\lianben_scanAngle\f{i+1}.log").mol
    mol.create_bonds()
    mol.add_bond(a1, a2)
    centerAtom=mol.atom(a1)
    aroundAtom=mol.atom(a2)
    lengths.append(mol.get_bond(a1, a2).length)

    caler1=piBondOrder.Calculator(mol)
    order1=caler1.calculate(centerAtom, aroundAtom)['data']['order']
    orders1.append(order1)
    print(order1)

#     caler3=piSelectOrder.Calculator(mol)
#     order3=caler3.calculate(centerAtom, aroundAtom)['data']['order']
#     print(order3)
#     orders3.append(order3)
# np.save('orders3.npy', np.array(orders3))
np.save('orders1.npy', np.array(orders1))
# plt.plot(np.arange(len(orders1)),np.array(orders1))
