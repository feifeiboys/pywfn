from csv import reader
from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import numpy as np
from pywfn.atomprop import freeValence
from pywfn.readers import LogReader

path=r"D:\BaiduSyncdisk\gFile\C[CH2]3.log"
path=r"D:\BaiduSyncdisk\gFile\C=C\CH2=CH2.out"
path=r"D:\BaiduSyncdisk\gFile\scans\lianben\lianben_6-31G.log"
import numpy as np
import matplotlib.pyplot as plt
angles=[]
for i in range(36):
    path=rf"D:\BaiduSyncdisk\gFile\scans\lianben\lianben_scanAngle\f{i+1}.log"
    reader=LogReader(path)
    mol=reader.mol
    angle=mol.get_dihedralAngle(2,3,12,13)
    print(angle)
    angles.append(angle)

plt.plot(np.arange(len(angles)),np.array(angle))