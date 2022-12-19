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

def zip(files,name):
    zipFile=zipfile.ZipFile(f'{name}.zip','w')
    for each in files:
        zipFile.write(each)
    
def count(files):
    total=0
    for each in files:
        lineNum=fileLines(each)
        print(f'{each:<40}{lineNum}')
        total+=lineNum
    print(f'{"total":<40}{total}')

def save(files):
    contents=[]
    for each in files:
        with open(each,'r',encoding='utf-8') as f:
            contents.append(f.read())
    with open('源代码.txt','w',encoding='utf-8') as f:
        f.write('\n'.join(contents))

opts=[
    'pywfn',
    'app',
    'manager',
    'main.py',
    'main.bat'
]
# 定义需要排除的文件类型
rms=[
    '__pycache__',
    '.pyc',
    '.ui',
    '.json',
    '.csv'
]

files=[]
lines=[]
for opt in opts:
    get(Path(opt))
# zip(files,'pywfn')
count(files)
# save(files)


files=[]
opts.append('env')
for opt in opts:
    get(Path(opt))
# zip(files,'pywfn_env')
