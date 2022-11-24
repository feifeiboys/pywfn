from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
# 设定好执行库所必须的文件
import importlib
import os
libSource='https://pypi.tuna.tsinghua.edu.cn/simple'
def chkPkgs(pkg):
    """检查所需的包是否完整,不完整的话就下载"""
    lib,name = pkg
    try:
        importlib.import_module(name)
    except:
        os.system(f'env\python.exe -m pip install {lib} -i {libSource}')
pkgs=[
    ['numpy','numpy'],
    ['pyside6','PySide6'],
    ['pyyaml','yaml'],
    ['pandas','pandas'],
    ['colorama','colorama'],
    ['numba','numba'],
    ['Pillow','PIL'],
    ['tqdm','tqdm'],
    ['pyperclip','pyperclip'],
    ['pyvista','pyvista'],
    ['pyvistaqt','pyvistaqt'],
]
# 导入与安装
# 安装时的名称和导入时的名称是不一样滴
for pkg in pkgs:chkPkgs(pkg)
os.system('clear')
def run(opt):
    if opt=='1':
        import pywfn
        pywfn.setting.IF_DEBUG=False
        pywfn.run()
    elif opt=='2':
        import app
        app.run()
    elif opt=='3':
        import manager
        manager.run()
    elif opt=='4':
        from manager import game

if len(sys.argv)>1:run(sys.argv[1])
else:
    print("""
    1.pywfn命令行
    2.窗口程序
    3.文件管理器
    """)
    opt=input('请选择需要启动的应用:')
    run(opt)