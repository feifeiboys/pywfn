from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pywfn.readers import LogReader
from pywfn.data import Basis
reader=LogReader("examples\mols\CH2O.log")
# mol=reader.mol
# for atom in mol.atoms:
#     print(atom.idx,atom.obtRange)
# print(mol.CM.shape)