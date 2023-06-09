import json
import os
from typing import *
import shutil
class settingManager:
    def __init__(self) -> None:
        """不要改变默认的设置文件，克隆一份方便还原"""
        self.cwd=cwd=os.path.join(os.getcwd(),'pywfnW')
        print(cwd)
        if not os.path.exists(self.local('setting.json')):
            shutil.copyfile(self.local('rawSetting.json'),self.local('setting.json'))
        self._setting:Dict=self.read()

    def local(self,path):
        """将相对路径转为绝对路径"""
        return os.path.join(self.cwd,path)

    def read(self):
        """读取设置文件"""
        with open(self.local('setting.json'),'r',encoding='utf-8') as f:
            return json.loads(f.read())

    def save(self):
        """保存设置信息"""
        with open(self.local('setting.json'),'w',encoding='utf-8') as f:
            f.write(json.dumps(self._setting))


    @property
    def lastOpenFilePath(self):
        """最后一次打开文件的位置(文件夹)"""
        return self._setting['lastOpenFilePath']
    
    @lastOpenFilePath.setter
    def lastOpenFilePath(self,value):
        if not isinstance(value, str):
            raise
        self._setting['lastOpenFilePath']=value
        self.save()


