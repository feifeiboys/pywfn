from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
from pywfn.readers import LogReader
from pywfn.atomprop import freeValence
from pyvista import examples
import pyvista as pv
bolt_nut = examples.download_bolt_nut()
pl = pv.Plotter()
_ = pl.add_volume(bolt_nut, cmap="coolwarm")
pl.show()