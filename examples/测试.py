from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pywfn.readers import LogReader
from pywfn.data import Basis
from pywfn.atomprop import mullikenSpin,piSpin
from pywfn.bondorder import piSM,piDM
import numpy as np

bond=(3,12)
orders=np.zeros(shape=(37,2))
for i in range(37):
    path=rf'D:\BaiduSyncdisk\gFile\scans\lianben\lianben_scanAngle\f{i+1}.log'
    reader=LogReader(path)
    mol=reader.mol
    print(i)
    caler=piSM.Calculator(mol)
    order=caler.calculate(*bond)
    orders[i,0]=order
    
    caler=piDM.Calculator(mol)
    order=caler.calculate(*bond)
    orders[i,1]=order
print(orders)
np.save('联苯Scan.npy',orders)

# path='D:\BaiduSyncdisk\gFile\C=C\CH2=CH2.out'
# reader=LogReader(path)
# mol=reader.mol
# caler=piSM.Calculator(mol)
# print(caler.calculate(1,4))
# print(mol.atom(1).get_Normal())
# for i in range(8):
#     print(i+1,mol.atom(1).get_obtWay(i))