from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
from hfv.readers import Reader
from hfv.calculators import piBondOrder,mayerBondOrder
import matplotlib.pyplot as plt
orders=[]
lengths=[]
a1,a2=[1,4]
for i in range(22):
    print(i+1)
    path=f"E:/BaiduSyncdisk/gFile/C=C/CH2=CH2_Scan/f{i+1}.log"
    reader=Reader(path)
    mol=reader.mol
    mol.create_bonds()
    mol.add_bond(a1, a2)
    centerAtom=mol.atoms[a1]
    aroundAtom=mol.atoms[a2]
    caler=mayerBondOrder.Caculater(mol)
    res=caler.calculate(centerAtom, aroundAtom)
    orders.append(res)
    lengths.append(mol.get_bond(a1, a2).length)
    print(res)
plt.plot(lengths,orders)
plt.show()