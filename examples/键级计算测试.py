

# 指定文件以及要计算的键,计算键级
from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

from hfv.readers import logReader
from hfv.calculators import piBondOrder
import matplotlib.pyplot as plt
lengths=[]
orders=[]

a1,a2=[1,4]
for i in range(22):
    path=path=f"E:/BaiduSyncdisk/gFile/C=C/CH2=CH2_Scan/f{i+1}.log"
    
    mol=logReader(path).mol
    mol.create_bonds()
    mol.add_bond(a1, a2)
    mol.createAtomOrbitalRange()
    
    centerAtom=mol.atoms[a1]
    aroundAtom=mol.atoms[a2]
    caler=piBondOrder.Calculator(mol)
    order=caler.calculate(centerAtom, aroundAtom)['data']['order']
    lengths.append(mol.get_bond(a1, a2).length)
    orders.append(order)

plt.plot(lengths,orders,'-.*')
plt.show()