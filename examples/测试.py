from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pandas as pd
import numpy as np

from pywfn.readers import FchReader

reader=FchReader('examples/mols/C[CH2]3.fchk')
