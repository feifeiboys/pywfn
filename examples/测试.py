from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pandas as pd
import numpy as np

from pywfn.readers import FchReader,LogReader
from pywfn.bondorder import piDM

path='examples/mols/CH2=CH2.out'
reader=LogReader(path)
mol=reader.mol
caler=piDM.Calculator(mol)
res=caler.calculate(mol.atom(1),mol.atom(4))
print(res)