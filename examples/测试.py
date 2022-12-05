from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))

from pywfn.base import Basis
basis=Basis('6-31G*')