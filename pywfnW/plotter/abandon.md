```python
elif showType=='surfP':
    valuesUnits = np.divide(values, np.abs(values), out=np.zeros_like(values), where=values!=0)
    values=np.where((values>self.isoValue) | (values<-self.isoValue),1.,0.)
    values[[0,-1],:,:]=0 # 某一个维度的最前方和最后方设为0
    values[:,[0,-1],:]=0
    values[:,:,[0,-1]]=0

    values0=np.zeros_like(values)
    # --- 问题就出现在这一块
    values0[ 1:,:,:]+=values[:-1,:,:]
    values0[:-1,:,:]+=values[ 1:,:,:]

    values0[:, 1:,:]+=values[:,:-1,:]
    values0[:,:-1,:]+=values[:, 1:,:]

    values0[:,:, 1:]+=values[:,:,:-1]
    values0[:,:,:-1]+=values[:,:, 1:]

    valuesR=values+values0 #原来的点与周围方向的点的加和
    valuesR=np.where(valuesR>=7,0,valuesR) #满足条件的为1，不满足条件的为0
    valuesR*=valuesUnits #为所有值赋予单位，正1或负1
    valuesR=valuesR.flatten() #拉平
    # valuesR=values.flatten()
    idxsP=np.argwhere(valuesR>0).flatten()
    idxsN=np.argwhere(valuesR<0).flatten()
    posP=pos[idxsP]
    posN=pos[idxsN]
    self.add_cloud(posP,'red',f'cloud-P-{name}')
    self.add_cloud(posN,'blue',f'cloud-N-{name}')
```

```python
class Clouds: #定义点云类型
    def __init__(self,atoms:List[Atom],canvas:Canvas) -> None:
        self.canvas=canvas
        # 不管选择哪几个原子，只需要按照原子序号排序
        idxs=[str(atom.idx) for atom in atoms]
        self.name=f'{self.canvas.selectedOrbital}-{",".join(idxs)}'
        if self.canvas.app is not None:
            self.canvas.app.ui.listWidget_clouds.addItem(self.name)
        self.atoms=atoms
        coords=np.array([atom.coord for atom in atoms])
        self.centerPos=np.mean(coords,axis=0)
        self.radius=np.linalg.norm(np.max(np.abs(coords-self.centerPos),axis=0))+1
        self.positiveCloud=None
        self.negativeCloud=None
        self.gridPoints=utils.get_gridPoints(self.radius,0.1,ball=True)
        self.addCloud()
        self.cloudRang:float=0.0
        
    def createData(self):
        datas=[]
        for atom in self.atoms:
            centerPos=self.centerPos.reshape(3,1)
            aroundPos=self.gridPoints+centerPos
            data=utils.posan_function(
                centerPos=centerPos,
                aroundPos=aroundPos,
                paras=atom.standardBasis,
                ts=atom.pLayersTs(self.canvas.selectedOrbital)
                )
            datas.append(data)
        datas=np.array(datas).sum(axis=0)
        return datas

    def addCloud(self):
        self.cloudRange=self.canvas.cloudRange
        values=self.createData()
        points=self.gridPoints+self.centerPos.reshape(3,-1)
        data=np.concatenate([points,values]).T
        positiveValues,negativeValues=util.splited(data)
        positiveValues=util.limited(positiveValues,self.canvas.cloudRange)
        negativeValues=util.limited(negativeValues,self.canvas.cloudRange)

        positiveValues=positiveValues.reshape(-1,4)[:,:-1]
        negativeValues=negativeValues.reshape(-1,4)[:,:-1]

        positivePoints=util.get_borders(positiveValues) # 获取边界点
        negativePoints=util.get_borders(negativeValues)

        positivePoints=np.concatenate([positivePoints,self.centerPos.reshape(1,3)]) #为了使数组不为空，需要添加原点
        negativePoints=np.concatenate([negativePoints,self.centerPos.reshape(1,3)])
        print('数据点',len(positivePoints),len(negativeValues))
        positiveCloud=pv.PolyData(positivePoints)
        negativeCloud=pv.PolyData(negativePoints)

        # print('添加点云')
        if len(positiveValues)>0:
            self.positiveCloud=self.canvas.plotter.add_mesh(positiveCloud,color='#c12c1f',opacity=0.5,
                reset_camera=False,name=f'cloud-positive-{self.name}',pickable=False)
        if len(negativeValues)>0:
            self.negativeCloud=self.canvas.plotter.add_mesh(negativeCloud,color='#84a729',opacity=0.5,
                reset_camera=False,name=f'cloud-negative-{self.name}',pickable=False)

    def setVisible(self,name):
        # print(f'{name=},{self.name=}')
        if name==self.name:
            if self.positiveCloud:self.positiveCloud.SetVisibility(True)
            if self.negativeCloud:self.negativeCloud.SetVisibility(True)
        else:
            if self.positiveCloud:self.positiveCloud.SetVisibility(False)
            if self.negativeCloud:self.negativeCloud.SetVisibility(False)
```