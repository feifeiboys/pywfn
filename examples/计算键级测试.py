from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pywfn.readers import logReader
from pywfn.calculators import piBondOrder,piSelectOrder
orders1=[]
orders2=[]
lengths=[]
for i in range(22):
    mol=logReader(f"E:\\BaiduSyncdisk\\gFile\\C=C\\CH2=CH-CH=CH2_scanAngle\\f{i+1}.log").mol
    mol.create_bonds()
    # pd.DataFrame(mol.PM*mol.SM).to_csv('PS.csv')

    # print(np.sum(mol.PM*mol.SM,axis=0))
    mol.add_bond(1, 3)
    centerAtom=mol.atoms[1]
    aroundAtom=mol.atoms[3]
    
    caler1=piBondOrder.Calculator(mol)
    caler2=piSelectOrder.Calculator(mol)
    order1=caler1.calculate(centerAtom, aroundAtom)['data']['order']
    order2=caler2.calculate(centerAtom, aroundAtom)['data']['order']
    # print(res)
    lengths.append(mol.get_bond(1, 3).length)
    orders1.append(order1)
    orders2.append(order2)
print(orders1)
print(orders2)
plt.plot(np.arange(len(orders1)),np.array(orders1))
# plt.plot(np.arange(len(orders2)),np.array(orders2))
plt.show()
