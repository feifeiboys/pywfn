from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
from pywfn.readers import LogReader
from pywfn.molprop import MolProp
from pywfn.multiprop import Fukui
reader=LogReader('examples/mols/CH2O.log')
readerN=LogReader('examples/mols/CH2ON.log')
readerP=LogReader('examples/mols/CH2OP.log')
fukui=Fukui(readerN.mol,reader.mol,readerP.mol)
for i in range(4):
    print(fukui.fn(i+1),fukui.fp(i+1))