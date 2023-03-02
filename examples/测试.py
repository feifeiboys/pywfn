import pyvista as pv
import numpy as np
import vtk

points=np.array([
    [1,0,0],
    [0,0,1],
    [-1,0,0],
    [0,0,-1]
],dtype=np.float32)
labels=['1','2','3','4']
plotter=pv.Plotter()

actor=plotter.add_point_labels(points=points,labels=labels)
# textMapperC = vtk.vtkTextMapper()
# textMapperC.SetInput("This is\nmulti-line\ntext output\n(centered)")
# tprop = textMapperC.GetTextProperty()
# # tprop.ShallowCopy(multiLineTextProp)
# tprop.SetJustificationToCentered()
# tprop.SetVerticalJustificationToCentered()
# # tprop.SetColor(colors.GetColor3d("DarkGreen"))
# actor.SetMapper(textMapperC)
actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
actor.GetPositionCoordinate().SetValue(0.5, 0.5)
print(actor)
plotter.show()