import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
from .scripy import Caculater
import os
from ..utils import get_nums
class Page:
    def __init__(self, program):
        self.program = program
        self.window = tk.Toplevel()
        pageWidth,pageHeight=self.program.config['pageWidth'],self.program.config['pageHeight']
        screenWidth,screenHeight=self.window.winfo_screenwidth(),self.window.winfo_screenheight()
        self.window.geometry(f'{pageWidth}x{pageHeight}+{int(screenWidth/2)}+{int(screenHeight/2-pageHeight/2)}')
        self.window.title(f'Calculate free valence:{os.path.basename(program.log_path)}')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.caculater = Caculater(program)

    def init_variable(self):
        self.if_save = tk.IntVar()

    def init_component(self):
        tk.Label(self.window, text='Enter the central atom number').place(x=0, y=100, anchor='nw')
        self.entry1 = tk.Entry(self.window, show=None, width=200)
        self.select_button=ttk.Button(self.window,text='select',command=lambda:threading.Thread(target=self.select).start())
        self.caculate_button = ttk.Button(self.window, text='start', command=lambda:threading.Thread(target=self.caculate).start(),bootstyle=(SECONDARY,OUTLINE))

    def set_conponent_pos(self):
        self.entry1.place(x=0, y=150, anchor='nw')
        self.select_button.place(x=240,y=400,anchor='center')
        self.caculate_button.place(x=240, y=500, anchor='center')

    def run(self):
        self.window.mainloop()

    def num2str(self, nums):
        for i in range(len(nums)): nums[i] = str(nums[i])
        return nums

    def get_select(self): #用户可以读取修改过的信息，所以要在输出窗口中重新读取
        texts=self.program.log_window_text.get(1.0,'end')
        all_obtials=self.program.Data.atoms[0]['obtials']
        begin=0
        end=0
        lines=texts.split('\n')
        for i,line in enumerate(lines):
            if line=='<'*50:
                begin=i
            if line=='>'*50:
                end=i
        contents=lines[begin+1:end]
        for each in contents:
            obtials_str=each.split(':')[1]
            if len(obtials_str)==0:
                obtials=[]
            else:
                obtials=[int(each)-1 for each in obtials_str.split(',')]
            if self.program.Data.obtial_type==0:
                key=each.split(':')[0]
                
                center=int(key.split('->')[0])-1
                around=int(key.split('->')[1])-1
                self.selectedObtials[f'{center}-{around}-O']=obtials
            elif self.program.Data.obtial_type==1:
                key=each.split(':')[0][:-1]
                center=int(key.split('->')[0])-1
                around=int(key.split('->')[1])-1
                obtialType=each.split(':')[0][-1]
                if obtialType=='α':
                    self.selectedObtials[f'{center}-{around}-O']=obtials
                elif obtialType=='β':
                    self.selectedObtials[f'{center}-{around}-O']+=[each+len(all_obtials)//2 for each in obtials]
        self.caculater.selectedObtials=self.selectedObtials


    def select(self):
        self.program.log_window_text.insert('end','<'*50+'\n')
        centers = get_nums(self.entry1.get())
        all_obtials=self.program.Data.atoms[0]['obtials']
        res=self.caculater.select(centers) # 获得挑选出的轨道，并将挑选出的轨道按照格式输出
        self.selectedObtials=res
        for key in res.keys():
            center=int(key.split('-')[0])+1
            around=int(key.split('-')[1])+1
            obtialType=key.split('-')[2]
            if obtialType=='O':
                if self.program.Data.obtial_type==0:
                    self.program.log_window_text.insert('end',f'{center}->{around}:'+','.join(f'{each+1}' for each in res[key])+'\n')
                elif self.program.Data.obtial_type==1:
                    #将轨道分为两种类型
                    Aobtials=[]
                    Bobtials=[]
                    for each in res[key]:
                        if each<len(all_obtials)/2:
                            Aobtials.append(each)
                        else:
                            Bobtials.append(each)
                    self.program.log_window_text.insert('end',f'{center}->{around}α:'+','.join(f'{each+1}' for each in Aobtials)+'\n')
                    self.program.log_window_text.insert('end',f'{center}->{around}β:'+','.join(f'{each+1-len(all_obtials)//2}' for each in Bobtials)+'\n')
        self.program.log_window_text.insert('end','>'*50+'\n')
    def caculate(self):  # 获取用户输入的参数
        centers = get_nums(self.entry1.get())
        self.get_select()
        self.caculater.caculate(centers)
