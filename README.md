# logProcess
#### 介绍
处理高斯输出log文件，计算键级自由价

#### 更新日志 

- 21.12.17
  - 直接令每个原子所有轨道的前一半不参与轨道的挑选，增加对α和β轨道的支持  
- 21.12.18
  - 支持手动输入轨道，如果不输入则程序自动挑选出轨道，不同周围原子间用|分割，不同轨道用α、β分割
  - 输入数字的时候添加对中文逗号分割的支持
  - 某个轨道中心到周围和周围到中心键轴上的十个值都算出来，然后有一个最大值小于0.01即为符合条件的轨道
- 21.12.22
  - 修复无法挑选原子和轨道生成excel的BUG

#### 软件架构
软件分为一下几个主要部分  
- main.py 仅负责组件间的关联以及信息的打印
- logReader.py 负责程序对log/out文件的读取  
- logCaculate.py 负责进行相关的量化计算  
- logWriter.py 负责保存读取和计算的结果  
- pages/ 存储程序的扩展界面
  - bond_level 计算键级页面
  - save_obtial 保存轨道页面
- data.json 存储预设数据
- logs 存储每次程序运行时的日志文件

#### 基础页面架构
```python
import tkinter as tk
class Page:
    def __init__(self,program) -> None:
        self.program=program
        self.window = tk.Tk()
        self.window.geometry('480x640')
        self.window.title('title')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
    def init_variable(self):  # 定义tkinter变量
        pass

    def init_component(self): # 定义tkinter组件
        pass

    def set_conponent_pos(self): # 定义tkinter组件位置
        pass

    def run(self): # 运行页面
        self.window.mainloop()
```

#### 安装教程
1.  如果电脑上有python,第一次运行是需要输入命令  
    pip install -r requirements.txt
2.  如果电脑上没有python,则可以下载python39嵌入版到文件夹根目录并解压，然后双击start.bat即可运行程序  
    >链接：https://pan.baidu.com/s/1-NNkgzEtnVZDfj_zR1OQ1A   
    提取码：fhg1 --来自百度网盘超级会员V3的分享

#### 使用步骤(以萘为例)
1. 运行程序
![运行程序](/imgs/运行程序.png)
2.  `open`->打开需要处理的`log`或`out`文件
![读取文件](/imgs/读取文件后.png)
3.  在窗口右侧指定原子和轨道，用`-`和`,`分隔
![制定原子](/imgs/输入原子编号.png)
4.  点击`计算轨道和键级`
![计算结果](/imgs/计算键级.png)
#### 程序中用到的公式

- #### 计算原子周围某一点的函数值
$N_i=\left ( \frac {2\times \alpha _i}{\pi }  \right ) ^ {3/4} \times 2\times \sqrt{\alpha _i} $

$\phi _{x,i}=N_n \times (x-x_n)\times e^{-\alpha _i(r-R_A)^2}$

$\phi _{y,i}=N_n \times (y-y_n)\times e^{-\alpha _i(r-R_A)^2}$

$\phi _{z,i}=N_n \times (z-z_n)\times e^{-\alpha _i(r-R_A)^2}$

$(r-R_A)^2=(x-x_n)^2+(y-y_n)^2+(z-z_n)^2$

$\phi _{p,x}=c_1\times  \phi _{x,1}+c_2\times  \phi _{x,2}+c_3\times  \phi _{x,3}+c_4\times  \phi _{x,4}$

$\phi _{p,y}=c_1\times  \phi _{y,1}+c_2\times  \phi _{y,2}+c_3\times  \phi _{y,3}+c_4\times  \phi _{y,4}$

$\phi _{p,z}=c_1\times  \phi _{z,1}+c_2\times  \phi _{z,2}+c_3\times  \phi _{z,3}+c_4\times  \phi _{z,4}$

$f=p_x\times \phi_{p,x}+p_y\times \phi_{p,y}+p_z\times \phi_{p,z}$

其中 $i$ 代表第几个 $\alpha$ 和 $c$ ，$n$ 代表第几个原子，x,y,z即为原子周围某一点的坐标

#### 存在的问题
- π轨道挑不准
- 贡献正负

#### 功能及其流程
##### 计算键级
- 用户输入需要计算键级的原子
- 程序判断与指定原子连接的原子
- 循环每个中心原子
  - 循环每个相连原子
    - 循环每个轨道
      - 判断当前轨道是否为π轨道，挑选出π轨道
  - 计算两个原子之间的键级
- 计算中心原子与周围原子间的所有键级
- 用基准物键级减去所有键级为自由价

#### 技术规范
- 在页面脚本中不进行