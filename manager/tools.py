import random
import yaml
import os
import hashlib
from pathlib import Path
from shutil import copyfile
from typing import *
from . import utils
from .draw import saveImg
from pywfn.readers import LogReader

def get_yaml(path)->dict:
    with open(path,'r',encoding='utf-8') as f:
        return yaml.load(f,Loader=yaml.Loader)

def set_yaml(path,data):
    with open(path,'w',encoding='utf-8') as f:
        yaml.dump(data,f)

class Tools:
    def __init__(self) -> None:
        self.confifPath=Path(__file__).parent/'config.yml'
        self.config=self.get_config()
        self.check()
        self.infos=Infos(self)
    def check(self):
        """
        有时候需要为程序添加一些新的功能，就需要添加一些新的记录属性
        """
        if self.config["storagePath"]=='None': # 初始化存储路径的绝对位置
            self.config['storagePath']=Path(__file__).parent/'storages'

    def get_config(self):
        """获取配置信息"""
        return get_yaml(self.confifPath)
    
    def set_config(self):
        """保存并更新配置信息"""
        set_yaml(self.confifPath,self.config)
        self.config=self.get_config()

    def create_file(self,path):
        """
        创建一个本地文件
        文件名是随机的,内部包含一个yml文件用来保存文件的信息
        """
        # 获取文件哈希值
        path=Path(path)
        fileHash=utils.get_fileHash(path)
        if self.infos.exists(fileHash):
            print('相同的文件已经存在')
            return
        print(f'{fileHash=}')
        # 随机生成一个文件名
        name=utils.get_randomName()
        # 创建文件夹
        folder=Path(__file__).parent/self.config["storagePath"]/f'{name}'
        os.mkdir(folder)
        # 将文件拷贝到文件夹中
        copyfile(path,folder/path.name)

        self.infos.add(folder,update=True)

class Infos:
    """存储所有log文件的信息,实例化的时候会准备好已经存在的信息"""
    def __init__(self,tools:Tools) -> None:
        self.data:List[Info]=[]
        self.tools=tools
        self.update()
    
    def add(self,folder:str,update=False):
        """添加info,检查是否已经存在,已经存在的话就不添加了"""
        info=Info(folder)
        if update:info.update()
        self.data.append(info)
    
    def exists(self,hash):
        """根据哈希值判断文件是否存在"""
        for each in self.data:
            if each.hash==hash:
                return True
        return False
    
    def update(self):
        """获取已存储文件的信息"""
        storagePath=self.tools.config["storagePath"]
        for folder in Path(storagePath).iterdir():
            self.add(folder)

    def __getitem__(self,item)->"Info":
        return self.data[item]
    
    def __repr__(self) -> str:
        return f'{len(self.data)}'
    
class Info:
    def __init__(self,folder:Path) -> None:
        """
        一个Info对象对应一个info.yml文件
        所以初始化对象的时候只需要传入文件所在的文件夹
        """
        self.folder=folder

        self.path=''
        self.hash=''
        self.name:str=''
        self.route=None
        self.symbols:List[str]=[]
        self.atomNum:int=0 # 原子的数量
        self.coords=[]
        # 文件属性
        self.st_size:int=None #文件大小
        self.st_ctime:int=None #文件创建时间
        self.st_mtime:int=None #文件修改时间
        self.st_atime:int=None #文件修改时间

        self.info=get_yaml(self.folder/'info.yml')
        self.check()
        with open(Path(__file__).parent/'prop.md','r',encoding='utf-8') as f:
            self.mdTemplate=f.read()
    
    def get_logPath(self):
        """获取当前文件夹下的log文件的路径"""
        for file in self.folder.iterdir():
            if file.suffix in ['.log','.out']:
                return file
        raise
    
    def check(self):
        """检查属性是否完整"""
        logPath=self.get_logPath()
        # 获取log文件的一些基本信息
        self.st_size=logPath.stat().st_size #文件大小
        self.st_ctime=logPath.stat().st_ctime #创建时间
        self.st_mtime=logPath.stat().st_mtime #修改时间
        self.st_atime=logPath.stat().st_atime #修改时间
        
        if not (self.folder/'info.yml').exists(): # 如果还不存在yml文件,则生成一个yml文件
            logHash=utils.get_fileHash(logPath)
            data={
                "path":f'{logPath}',
                "hash":logHash,
                "name":f'{logPath.name}',
                "route":None
            }
            set_yaml(self.folder/'info.yml',data)
        if 'labels' not in self.info.keys():
            self.info['labels']=[]
            self.save()
        if 'note' not in self.info.keys():
            self.info['note']=''
            self.save()
        
        
        
        # 有些计算很快的属性可以经常改变(如果检测到现在文件的哈希值之前文件的哈希值不同,则需要更新信息)
        self.set_prop()
    def save(self):
        """保存本地配置信息"""
        set_yaml(self.folder/'info.yml',self.info)
    def update(self):
        """
        生成一些属性需要调用pywfn才能属性
        用户手动触发或者新添加文件时触发
        存储哪些属性呢?原子数量、原子坐标
        """
        info=get_yaml(self.folder/'info.yml')
        logPath=self.get_logPath()
        reader=LogReader(logPath)
        mol=reader.mol
        saveImg(reader.mol,self.folder/'mol.png')
        info['atomSymbol']=[atom.symbol for atom in mol.atoms()] # 存储所有的原子符号
        info['atomCoord']=mol.coords.tolist() #存储原子坐标
        info['O_orbital']=len(mol.O_orbitals) #占据分子轨道数量
        info['V_orbital']=len(mol.V_orbitals) #空分子轨道数量
        self.info=info
        self.save()


    
    def set_prop(self):
        """将字典的属性设置为类的属性"""
        for key,value in self.info.items():
            if key=='name':
                self.name=value
            elif key=='path':
                self.path=value
            elif key=='hash':
                self.hash=value
            elif key=='route':
                self.route=value
            elif key=='atomSymbol':
                self.symbols=value
                self.atomNum=len(value)
            elif key=='atomCoord':
                self.coords=value
            elif key=='O_orbital':
                self.ooNum=value
            elif key=='V_orbital':
                self.voNum=value
            
    def __repr__(self) -> str:
        return f'{self.name};{self.hash}'
    
    def prop(self,propName:str):
        """根据属性名返回属性值"""
        self.get
    
    def md(self):
        msg={}
        msg['NAME']=self.name
        msg['ATOM_NUM']=f'{len(self.symbols)}'
        if self.ooNum is not None and self.voNum is not None:
            msg['TO_NUM']=f'{self.ooNum+self.voNum}'
            msg['OO_NUM']=f'{self.ooNum}'

        if self.coords is not None:
            msg['COORD']=''
            for s,(x,y,z) in zip(self.symbols,self.coords):
                msg['COORD']+=f'{s:<3}{x:<8.4f}{y:<8.4f}{z:<8.4f}  \n'

        
        for key,value in msg.items():
            self.mdTemplate=self.mdTemplate.replace(key,value)
        return self.mdTemplate