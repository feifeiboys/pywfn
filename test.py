import numpy as np

import pyvista as pv
from pyvista import examples
grid = examples.load_hydrogen_orbital(3, 2, -2)
pl = pv.Plotter()

print(pl.camera.position)
print(pl.camera.focal_point)
print(pl.camera.up)