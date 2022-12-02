from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pandas as pd
import numpy as np

from pywfn.readers import FchReader,LogReader
from pywfn.bondorder import piDM

path='examples/mols/CH2O.log'
reader=LogReader(path)
atom=reader.mol.atom(1)
v=atom.get_cloud(np.zeros((1,3)),5)
print(v)