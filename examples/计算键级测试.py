from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

import re
import numpy as np
from hfv.readers import logReader
from hfv.calculators import piBondOrder

mol=logReader('examples/CH2=CH2.out').mol

print(np.sum(mol.PM*mol.SM))
# centerAtom=mol.atoms[1]
# aroundAtom=mol.atoms[4]
# caler=piBondOrder.Calculator(mol)
# res=caler.calculate(centerAtom, aroundAtom)
# print(res)
