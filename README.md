# logProcess
#### 介绍
处理高斯输出log文件，计算键级自由价


#### 软件结构
软件分为一下几个主要部分  
- `main.py` 仅负责组件间的关联以及信息的打印
- `logReader.py` 负责程序对log/out文件的读取  
- `pages/` 存储程序的扩展界面
  - `bond_level` 计算键级页面
    - `page.py` 负责页面组织
    - `script.py` 负责计算
- `data.json` 存储预设数据
- `logs` 存储每次程序运行时的日志文件


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




#### 技术规范
- 在页面脚本中不进行计算

### 依赖包
- numpy
- pandas
- matplotlib
- sympy
- xlsxwriter
