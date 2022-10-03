from pathlib import Path
hfvPath=Path(__file__).parent.parent
import sys
sys.path.append(str(hfvPath))
from pywfn.tools import ScanSpliter

path=r"E:\BaiduSyncdisk\gFile\C=C\CH2=CH2_Scan.out"
tool=ScanSpliter(path=path)
tool.split()
