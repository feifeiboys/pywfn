from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
from hfv.readers import Reader
from hfv.calculators import piBondOrder,mayerBondOrder

path='examples/CH2=CH2.out'
reader=Reader(path)
mol=reader.mol
centerAtom=mol.atoms[1]
aroundAtom=mol.atoms[2]
caler=mayerBondOrder.Caculater(mol)
res=caler.calculate(centerAtom, aroundAtom)
print(res)