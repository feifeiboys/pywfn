from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import numpy as np
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
np.save('orders1.npy', np.array(orders1))