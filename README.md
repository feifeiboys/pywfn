# `pywfn` -- 基于python的波函数分析工具
将`pywfn`作为提供计算的模块(后端)  
用`pyside6`设计程序界面，`pyvista`实现分子可视化

设计上模仿vscode,可以打开多个页面  
每个文件用一个分子对象封装

App.py是程序的入口，主要页面及功能保存在app文件夹内
## 程序的功能
- 打开并读取文件
    - .log/.out
    - .fchk
- 显示读取到的信息，并且可视化分子
- 计算所需的性质
    - π-select-HMO键级
    - π-project-HMO键级
    - π-select-Mayer键级
    - π-project-Mayer键级
    - mayer键级
    - mulliken电荷
    - π电子
- 简单命令行交互
    - 插入箭头

## 使用方式
### GUI
运行App.py  
要显示的信息太多，GUI的方式好像确实不太方便
### Shell
使用ipython/python
```python
import pywfn
pywfn.runShell()
```
# todo
- 制作程序网站以及使用手册
- 可以为程序添加下载模块,当程序有一些小更新时,便可以自动并保存替换py文件,但是这个脚本文件本身无法更新,关键是程序的脚本文件要放到哪里合适
- 为了减小程序的体积，可以尽量使程序自带的python处于最小的体积(不含有任何额外包),当用户使用时再联网下载