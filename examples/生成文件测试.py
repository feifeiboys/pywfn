from pywfn.obj import File
from pywfn.tools import FileCreater
from pathlib import Path

path=r"E:\BaiduSyncdisk\gFile\others\wang\r2_d3.log"
mol=File(path).mol

folder=Path(path).parent
craetor=FileCreater(folder/'m0')
