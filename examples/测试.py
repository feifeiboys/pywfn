from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
from pywfn.readers import LogReader
from pywfn.atomprop import freeValence
reader=LogReader('examples/mols/CH2O.log')
mol=reader.mol
caler=freeValence.Calculator(mol)
res=caler.calculate(mol.atom(1))
print(res)