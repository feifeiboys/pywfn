"""
将需要的项目代码打包
"""
from pathlib import Path
import zipfile

class Tool:
    def __init__(self) -> None:
        self.opts=[
            'pywfn',
            'app',
            'manager',
            'main.py',
            'main.bat'
        ]
        # 定义需要排除的文件类型
        self.rms=[
            '__pycache__',
            '.pyc',
            '.ui',
        ]
    def get_files(self):
        self.files=[]
        for opt in self.opts:
            self.get(Path(opt))


    def zip(self,name):
        zipFile=zipfile.ZipFile(f'{name}.zip','w')
        print(len(self.files))
        for each in self.files:
            zipFile.write(each)
        
    def count(self):
        
        total=0
        self.rms+=['.csv','.json']
        self.get_files()
        for each in self.files:
            lineNum=self.fileLines(each)
            print(f'{each:<40}{lineNum}')
            total+=lineNum
        print(f'{"total":<40}{total}')

    def save(self,files):
        contents=[]
        for each in files:
            with open(each,'r',encoding='utf-8') as f:
                contents.append(f.read())
        with open('源代码.txt','w',encoding='utf-8') as f:
            f.write('\n'.join(contents))
    
    def fileLines(self,path):
        cwd=Path.cwd()
        filePath=cwd/path
        with open(filePath,'r',encoding='utf-8') as f:
            return len(f.readlines())

    def ifRm(self,path:str):
        for rm in self.rms:
            if rm in path:
                return True
        return False

    def get(self,path):
        
        if path.is_file(): #如果是文件夹
            path=str(path)
            if not self.ifRm(path): #如果不属于排除文件
                self.files.append(path)
        else:
            for each in path.iterdir():
                self.get(each)


tool=Tool()
# tool.zip('pywfn')
tool.count()
# count(files)
# save(files)