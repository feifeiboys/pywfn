from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pandas as pd
import numpy as np

from pywfn.readers import get_reader
from pywfn.bondorder import piSM,mayer

orders=[]
for i in range(37):
    path=rf"D:\BaiduSyncdisk\gFile\scans\dingerxi\dingerxiScan_Angle\f{i+1}.log"
    # print(i+1)
    reader=get_reader(path)
    mol=reader.mol
    caler=piSM.Calculator(mol)
    res=caler.calculate(mol.atom(1),mol.atom(3))
    print(res[0])
    orders.append(res[0])
pd.DataFrame(np.array(orders)).to_csv('piMayer.csv')