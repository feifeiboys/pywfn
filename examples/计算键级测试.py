from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pywfn.readers import logReader
from pywfn.calculators import piBondOrder,piSelectOrder,mayerBondOrder
orders1=[]
orders2=[]
orders3=[]
lengths=[]
a1,a2=[3,12]
for i in range(37):
    
    mol=logReader(f"E:\\BaiduSyncdisk\\gFile\\scans\\lianben\\lianben_scanAngle\\f{i+1}.log").mol
    mol.create_bonds()
    # pd.DataFrame(mol.PM*mol.SM).to_csv('PS.csv')

    # print(np.sum(mol.PM*mol.SM,axis=0))
    mol.add_bond(a1, a2)
    centerAtom=mol.atoms[a1]
    aroundAtom=mol.atoms[a2]
    lengths.append(mol.get_bond(a1, a2).length)
    
    # caler1=piBondOrder.Calculator(mol)
    # order1=caler1.calculate(centerAtom, aroundAtom)['data']['order']
    # orders1.append(order1)

    # caler2=piSelectOrder.Calculator(mol)
    # order2=caler2.calculate(centerAtom, aroundAtom)['data']['order']
    # orders2.append(order2)
    # print(i+1,order1)

    caler3=mayerBondOrder.Caculater(mol)
    order3=caler3.calculate(centerAtom, aroundAtom)
    orders3.append(order3)
# np.save('orders1.npy', np.array(orders1))
# np.save('orders2.npy', np.array(orders2))
np.save('orders3.npy', np.array(orders3))
# print(orders1)
# print(orders2)
# angles=[(i*10)+90 if i<=27 else i*10-270 for i in range(37)]
# plt.title(f'Bond Order - Dihedral Angle')
# plt.xlabel('Dihedral Angle')
# plt.ylabel('Bond Order')
# plt.xticks(angles)
# plt.plot(np.arange(len(orders1)),np.array(orders1))
# # plt.plot(np.arange(len(orders2)),np.array(orders2))
# plt.show()
