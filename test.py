import numpy as np

import pyvista as pv
from pyvista import examples
grid = examples.load_hydrogen_orbital(3, 2, -2)
pl = pv.Plotter()

sp=pl.add_mesh(pv.Sphere())
print(sp.prop)