from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pywfn.readers import LogReader
from pywfn.data import Basis
from pywfn.atomprop import mullikenSpin,piSpin
from pywfn.bondorder import piSM,piDM,mayer
import numpy as np

bond=(3,1)
orders=np.zeros(shape=(37,2))
for i in range(37):
    path=rf'D:\BaiduSyncdisk\gFile\scans\dingerxi\dingerxi_scanAngle\f{i+1}.log'
    reader=LogReader(path)
    mol=reader.mol
    print(i)
    caler=piSM.Calculator(mol)
    order=caler.calculate(*bond)
    orders[i,0]=order
    
    caler=mayer.Calculator(mol)
    order=caler.calculate(*bond)
    orders[i,1]=order
print(orders)
np.save('丁二烯Scan.npy',orders)
# from pywfn.maths import vector_angle
# from pywfn.bondorder.utils import judgeOrbital
# path=rf'D:\BaiduSyncdisk\gFile\C=C\CH2=C=C=CH2.log'
# reader=LogReader(path)
# mol=reader.mol
# caler=piDM.Calculator(mol)
# print(mol.atom(1).get_Normal())
# print(mol.atom(1).neighbors)
# print(caler.calculate(2,1))