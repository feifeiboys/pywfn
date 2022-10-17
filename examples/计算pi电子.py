from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

from pywfn.readers import get_reader
from pywfn.atomprop import piElectron
import numpy as np

electrons=[]
for i in range(37):
    path=rf"D:\BaiduSyncdisk\gFile\scans\lianben\lianben_scanAngle\f{i+1}.log"
    reader=get_reader(path)
    mol=reader.mol
    caler=piElectron.Calculator(mol)
    res=caler.calculate()
    print(sum(res))
    electrons.append(sum(res))
np.save('piElectronsDingerxi.npy',np.array(electrons))