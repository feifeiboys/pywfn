"""
此脚本用来读取fchk文件
fchk文件中有哪些属性是可以用到的？
"""
import re
import numpy as np
titleMatch='^(.{40}) {3}(.{1})(.{5})(.{12})$'
class FchReader:
    def __init__(self,path:str):
        self.path=path
        self.contents:Content=[]
        with open(self.path,'r',encoding='utf-8') as f:
            self.lines=f.read().split('\n')
        self.jobTitle:str=self.lines[0]
        self.jobType,self.jobMethod,self.jobBasis=re.match(r'(.{10})(.{30})(.{30})',self.lines[1]).groups()
        for idx in range(2,len(self.lines)):
            line=self.lines[idx]
            if re.match(titleMatch, line) is not None:
                self.contents.append(Content(idx+1, line))
    
    def __call__(self,title:str):
        title=title.ljust(40,' ')
        for each in self.contents:
            if each.title==title:
                return each.get(self)
        else:
            return None



class Content:
    def __init__(self,idx:int,line:str):
        self.idx=idx
        title,dataType,isArray,number=re.match(titleMatch,line).groups()
        self.title:str=title
        self.dataType:str=dataType
        self.isArray=True if 'N=' in isArray else False
        self.number:int=int(number)

    def get(self,reader):
        """读取其中内容"""
        if self.isArray:
            lineNum=self.number//5+1
            print(self.idx,lineNum)
            text='\n'.join(reader.lines[i] for i in range(self.idx,self.idx+lineNum))
            res=re.findall(r'-?\d+.\d+', text)
            return np.array(res)

    def __repr__(self):
        return f'{self.idx},{self.title},{self.dataType},{self.isArray},{self.number}\n'
