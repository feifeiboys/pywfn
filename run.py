from pathlib import Path
import sys
hfvPath=Path(__file__).parent.parent
sys.path.append(str(hfvPath))
# 设定好执行库所必须的文件
import importlib
import os
def run_shell():
    libs=[
        'numpy',
        'pandas',
        'numba',
        'colorama'
    ]
    for lib in libs:
        try:
            importlib.import_module(lib)
        except:
            os.system(f'python38\python.exe -m pip install {lib} -i https://pypi.tuna.tsinghua.edu.cn/simple')
    import pywfn
    from pywfn import setting
    setting.DEBUG=False
    pywfn.runShell()

def run_gui():
    import app

if len(sys.argv)>1:
    runType=sys.argv[1]
    if runType=='shell':
        run_shell()
    if runType=='gui':
        run_gui()
    if runType=='manager':
        from manager import main
        main.run()

if __name__=="__main__":
    ...
    from manager import main
    main.run()
    # from manager import game
