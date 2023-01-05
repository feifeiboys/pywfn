from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pywfn.readers import LogReader
from pywfn.data import Basis
from pywfn.atomprop import mullikenSpin,piSpin
reader=LogReader("examples\mols\CH2OP.log")
mol=reader.mol
# caler=mullikenSpin.Calculator(mol)
caler=piSpin.Calculator(mol)
caler.print()
# for atom in mol.atoms:
#     print(atom.idx,atom.obtRange)
# print(mol.CM.shape)