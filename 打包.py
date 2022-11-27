"""
将需要的项目代码打包
"""
from pathlib import Path
import zipfile


def fileLines(path):
    cwd=Path.cwd()
    filePath=cwd/path
    with open(filePath,'r',encoding='utf-8') as f:
        return len(f.readlines())

def ifRm(path:str):
    for rm in rms:
        if rm in path:
            return True
    return False

def get(path):
    
    if path.is_file(): #如果是文件夹
        path=str(path)
        if not ifRm(path): #如果不属于排除文件
            files.append(path)
    else:
        for each in path.iterdir():
            get(each)

def zip(files):
    zipFile=zipfile.ZipFile('pywfn.zip','w')
    for each in files:
        zipFile.write(each)
    
def count(files):
    total=0
    for each in files:
        lineNum=fileLines(each)
        print(f'{each:<40}{lineNum}')
        total+=lineNum
    print(f'{"total":<40}{total}')


opts=[
    'pywfn',
    'app',
    'manager',
    'main.py',
    'main.bat'
]
rms=[
    '__pycache__',
    '.pyc',
    '.ui'
]

files=[]
lines=[]


for opt in opts:
    get(Path(opt))


zip(files)
count(files)