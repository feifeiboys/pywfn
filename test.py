import numpy as np
import pyvista as pv
from sympy import sieve


ups = [
    [ 5.02299219e-01,  1.20940600e+00,  5.02299219e-01],
       [ 1.40535778e+00,  0.00000000e+00, -1.40535778e+00],
       [ 6.28036983e-15,  1.00000000e+00,  6.28036983e-15]
]
downs=[
     [ 1.91651278e+00,  1.20940600e+00,  1.91651278e+00],
       [-8.85578119e-03,  0.00000000e+00,  8.85578119e-03],
       [-6.28036983e-15, -1.00000000e+00, -6.28036983e-15]
]
atoms=[
    [1.209406  ,  0.698251  , 0.000000],
    [1.209406  , -0.698251  ,  0.000000],
    

]
size=50.0
plotter=pv.Plotter()
plotter.add_axes()
plotter.background_color='white'
plotter.add_points(np.array(ups).T,color='red',point_size=size/2,render_points_as_spheres=True)
plotter.add_points(np.array(downs).T,color='green',point_size=size/2,render_points_as_spheres=True)
plotter.add_points(np.array(atoms),color='black',point_size=size,render_points_as_spheres=True)
plotter.show()