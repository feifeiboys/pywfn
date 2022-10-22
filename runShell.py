from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
import pywfn
from pywfn import setting
setting.DEBUG=False
pywfn.runShell()