from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

from hfv.readers import logReader
from hfv.calculators import piMayerOrder

import matplotlib.pyplot as plt
orders=[]
idxs=[]
a1,a2=[1,4]
for i in range(22):
    path=f"E:/BaiduSyncdisk/gFile/C=C/CH2=CH2_Scan/f{i+1}.log"
    mol=logReader(path).mol
    mol.create_bonds()
    mol.add_bond(a1, a2)
    mol.createAtomOrbitalRange()
    centerAtom=mol.atoms[a1]
    aroundAtom=mol.atoms[a2]

    caler=piMayerOrder.Calculator(mol)
    res=caler.calculate(centerAtom, aroundAtom)
    idxs.append(mol.get_bond(a1, a2).length)
    orders.append(res)
    # print(res)
plt.plot(idxs,orders,'--*')
plt.show()
plt.savefig('piMayerOrder.png')