from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pandas as pd
import numpy as np

from pywfn.readers import FchReader,LogReader
from pywfn.bondorder import piDM

import basis_set_exchange as bse
import json
import re
from pywfn.base.basis import Basis
from pywfn.readers import LogReader

# basis=Basis('6-31g*')
# print(basis.get(6))

reader=LogReader('examples/mols/CH2O.log')
mol=reader.mol
atom=mol.atom(2)
# print(atom.pLayersTs(5))
print(mol.basis.name)
print(mol.basis.num(1))
# print(mol.basis.get(1))
mol.atom(2).cloud(2)