from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
from xlsxwriter import Workbook
import numpy as np
import pandas as pd
class Writer:
    def __init__(self,program) -> None:
        self.program=program
        #print(self.program.data)
        self.set_data()
    def set_data(self):
        Data=self.program.Data
        for each in dir(Data): #将Data对象的自定义属性赋值到self
            if each[0]!='_':
                setattr(self,each,getattr(Data,each))
    
    def save(self,atoms,orbitals): #保存文件
        path=self.program.log_path
        dataframe=pd.concat([self.atoms[each]['datas'].iloc[:,orbitals] for each in atoms])
        self.file_path = asksaveasfilename(defaultextension='.xlsx', title='保存文件',initialfile=os.path.splitext(os.path.basename(path))[0])
        dataframe.to_excel(self.file_path)
        self.program.log_window_text.insert('end', '文件保存成功\n')