from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
from hfv.obj import File
from hfv.calculators import piBondOrder,mayerBondOrder

file=File('examples/CH2=CH2.out')
mol=file.mol
centerAtom=mol.atoms[1]
aroundAtom=mol.atoms[4]
caler=mayerBondOrder.Caculater(mol)
res=caler.calculate(centerAtom, aroundAtom)
print(res.shape)
print(res.sum())