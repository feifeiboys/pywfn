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
import multiprocessing
from threading import Thread
from PySide6.QtWidgets import QFileDialog


def get_yaml(path)->dict:
    with open(path,'r',encoding='utf-8') as f:
        return yaml.load(f,Loader=yaml.Loader)

def set_yaml(path,data):
    with open(path,'w',encoding='utf-8') as f:
        yaml.dump(data,f)

class Tools:
    def __init__(self,window) -> None:
        self.window=window
        self.confifPath=Path(__file__).parent/'config.yml'
        self.config=self.get_config()
        self.check()
        self.infos=Infos(self)
    def check(self):
        """
        有时候需要为程序添加一些新的功能，就需要添加一些新的记录属性
        """
        if not Path(self.config["storagePath"]).exists():
            path=QFileDialog.getExistingDirectory(self.window,'选择存储位置')
            print(path)
            self.config['storagePath']=path
            self.set_config()

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
        print(f'{path=}')
        path=Path(path)
        fileHash=utils.get_fileHash(path)
        if self.infos.exists(fileHash):
            print('相同的文件已经存在')
            return
        # print(f'{fileHash=}')
        # 随机生成一个文件名
        name=utils.get_randomName()
        # 创建文件夹
        folder=Path(__file__).parent/self.config["storagePath"]/f'{name}'
        os.mkdir(folder)
        # 将文件拷贝到文件夹中
        copyfile(path,folder/path.name)

        info=self.infos.add(folder,update=True)
        return info

class Infos(list):
    """存储所有log文件的信息,实例化的时候会准备好已经存在的信息"""
    def __init__(self,tools:Tools) -> None:
        list.__init__([])
        self.tools=tools
        self.update()
    
    def add(self,folder:str,update=False)->"Info":
        """添加info,检查是否已经存在,已经存在的话就不添加了"""
        info=Info(folder)
        if update:info.update()
        self.append(info)
        return info
    
    def exists(self,hash):
        """根据哈希值判断文件是否存在"""
        for each in self:
            if each.hash==hash:
                return True
        return False
    
    def update(self):
        """获取已存储文件的信息"""
        storagePath=self.tools.config["storagePath"]
        for folder in Path(storagePath).iterdir():
            self.add(folder)

    def __getitem__(self,item)->"Info":
        return self[item]
    
    def __repr__(self) -> str:
        return f'{len(self)}'
    
class Info:
    # 设置一个文件应该有的属性,如果没有就补充,多余的话就删除
    props=['name','path','hash','route','symbols','coords','ooNum','voNum']
    #文件属性的md模板
    with open(Path(__file__).parent/'prop.md','r',encoding='utf-8') as f:
        mdTemplate=f.read()

    def __init__(self,folder:Path) -> None:
        """
        一个Info对象对应一个info.yml文件
        所以初始化对象的时候只需要传入文件所在的文件夹
        """
        self.folder=folder
        # 文件本的属性,文件名,路径,哈希值
        self.name:str=None
        self.path:str=None
        self.hash:str=None
        # 用户可自定义的属性,路由(分类),标签,备注
        self.route:str=None
        self.label:List[str]=None
        self.note:str=None
        # 根据文件内容的属性
        self.symbols:List[str]=None
        self.coords:List[List[float]]=None
        self.ooNum:int=None
        self.voNum:int=None
        
        self.check()
        # 文件状态属性,每次都重新生成,不需要存储
        
        self.st_size =self.logPath.stat().st_size #文件大小
        self.st_ctime=self.logPath.stat().st_ctime #创建时间
        self.st_mtime=self.logPath.stat().st_mtime #修改时间
        self.st_atime=self.logPath.stat().st_atime #修改时间
        

    def set_prop(self):
        """将字典的属性设置为类的属性"""
        # 对于属性名与yaml数据完全一致的，可以直接赋值
        for key,value in self.info.items():
            if key in self.props:
                setattr(self,key,value)
    
    def get_logPath(self):
        """获取当前文件夹下的log文件的路径"""
        for file in self.folder.iterdir():
            if file.suffix in ['.log','.out']:
                return file
        raise
    
    def check_prop(self,key,value): #添加目前不存在但又需要的属性
        if key not in self.info.keys():
            self.info[key]=value
            
    def check(self):
        """检查属性是否完整"""
        self.logPath=self.get_logPath()
        logHash=utils.get_fileHash(self.logPath)       
        if not (self.folder/'info.yml').exists(): # 如果还不存在yml文件,则生成一个yml文件            
            set_yaml(self.folder/'info.yml',{})
            self.update()
        self.info=get_yaml(self.folder/'info.yml')

        self.check_prop('path',f'{self.logPath}')
        self.check_prop('name',f'{self.logPath.name}')
        self.check_prop('hash',logHash)
        self.check_prop('route',None)
        self.check_prop('labels',[]) # 标签
        self.check_prop('note','') # 备注
        self.save()
        self.set_prop()

    def save(self):
        """保存本地配置信息"""
        set_yaml(self.folder/'info.yml',self.info)

    def update(self):
        """
        生成一些属性需要调用pywfn才能属性
        触发方式:
            1.用户手动触发
            2.新添加文件时触发
            3.文件哈希值改变触发
        存储属性:
            1.原子符号
            2.原子坐标
            3.轨道数量
            4.任务类型
        """
        info=get_yaml(self.folder/'info.yml')
        reader=LogReader(self.logPath)
        mol=reader.mol
        saveImg(reader.mol,self.folder/'mol.png')
        info['symbols']=[atom.symbol for atom in mol.atoms] # 存储所有的原子符号
        info['coords']=mol.coords.tolist() #存储原子坐标
        info['ooNum']=len(mol.O_obts) #占据分子轨道数量
        info['voNum']=len(mol.V_obts) #空分子轨道数量
        self.info=info
        self.save()

    def __repr__(self) -> str:
        return f'{self.name};{self.hash}'
    
    def prop(self,propName:str):
        """根据属性名返回属性值"""
        self.get
    
    def md(self):
        """返回文件属性markdowm字符串"""
        msg={}
        msg['NAME']=self.name
        atomNum=0
        if self.symbols is not None:atomNum=len(self.symbols)
        msg['ATOM_NUM']=f'{atomNum}'
        if self.ooNum is not None and self.voNum is not None:
            msg['TO_NUM']=f'{self.ooNum+self.voNum}'
            msg['OO_NUM']=f'{self.ooNum}'

        if self.symbols is not None and self.coords is not None:
            msg['COORD']=''
            for s,(x,y,z) in zip(self.symbols,self.coords):
                msg['COORD']+=f'{s:<3}{x:<8.4f}{y:<8.4f}{z:<8.4f}  \n'

        
        for key,value in msg.items():
            self.mdTemplate=self.mdTemplate.replace(key,value)
        return self.mdTemplate

def clear_info():
    config=get_yaml(Path(__file__).parent/'config.yml')
    storagePath=config['storagePath']
    for each in Path(storagePath).iterdir():
        os.remove(each/'info.yml')
