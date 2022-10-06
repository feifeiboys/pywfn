from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

from pywfn.readers import logReader
from pywfn.calculators import piMayerOrder

import matplotlib.pyplot as plt
import numpy as np
orders=[]
elects=[]
idxs=[]
a1,a2=[3,12]
for i in range(37):
    path=f"E:\\BaiduSyncdisk\\gFile\\scans\\lianben\\lianben_scanAngle\\f{i+1}.log"
    mol=logReader(path).mol
    mol.create_bonds()
    mol.add_bond(a1, a2)
    mol.createAtomOrbitalRange()
    centerAtom=mol.atoms[a1]
    aroundAtom=mol.atoms[a2]

    caler=piMayerOrder.Calculator(mol)
    order,elect=caler.calculate(centerAtom, aroundAtom)
    idxs.append(mol.get_bond(a1, a2).length)
    orders.append(order)
    elects.append(elect)
    # print(res)
plt.plot(np.arange(len(orders)),np.array(orders),'--*')
plt.plot(np.arange(len(elects)),np.array(elects),'--*')
plt.show()
plt.savefig('piMayerOrder.png')