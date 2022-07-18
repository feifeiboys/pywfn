import numpy as np
import pyvista as pv
centerNormal_12=np.array([0.0, 0.3071772573269765, 0.9516523170680963])
centerNormal_13=np.array([-0.2660232297955936, -0.15358863211575238, 0.9516523384587109])
centerNormal_14=np.array([0.2660232297955936, -0.15358863211575238, 0.9516523384587109])
centerPoint=np.array([.0,.0,.0])
plotter=pv.Plotter()
plotter.add_axes()
plotter.background_color='white'
plotter.add_arrows(centerPoint, centerNormal_12)
plotter.add_arrows(centerPoint, centerNormal_13)
plotter.add_arrows(centerPoint, centerNormal_14)
plotter.show()
