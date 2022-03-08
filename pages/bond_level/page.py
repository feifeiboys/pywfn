import re
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
import threading
import numpy as np
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
        self.window.title(f'计算轨道和键级{os.path.basename(program.log_path)}')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.caculater = Caculater(program)

    def init_variable(self):
        self.if_save = tk.IntVar()

    def init_component(self):
        tk.Label(self.window, text='输入中心原子编号').place(x=0, y=100, anchor='nw')
        self.entry1 = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入周围原子编号，用,和-分割:').place(x=0, y=200, anchor='w')
        self.get_connection_button = ttk.Button(self.window, text='自动获取', command=self.get_connection,style=(SECONDARY,OUTLINE))
        self.entry2 = tk.Entry(self.window, show=None, width=200)
        self.caculate_button = ttk.Button(self.window, text='计算轨道和键级', command=lambda:threading.Thread(target=self.caculate).start(),bootstyle=(SECONDARY,OUTLINE))

    def set_conponent_pos(self):
        self.entry1.place(x=0, y=150, anchor='nw')
        self.get_connection_button.place(x=220, y=200, anchor='center')
        self.entry2.place(x=0, y=250, anchor='nw')
        self.caculate_button.place(x=240, y=500, anchor='center')

    def run(self):
        self.window.mainloop()

    def num2str(self, nums):
        for i in range(len(nums)): nums[i] = str(nums[i])
        return nums
    def get_connection(self): #获得与中心原子相连的原子
        connections = []
        center_atom_indexs = get_nums(self.entry1.get())
        for center_atom_index in center_atom_indexs:
            res = self.caculater.get_connections(center_atom_index)
            connections.append(res)
        # 在信息框输入
        self.entry2.delete(0, 'end')
        self.entry2.insert(0, ';'.join([','.join([str(i + 1) for i in each]) for each in connections]))

    def caculate(self):  # 获取用户输入的参数
        centers = get_nums(self.entry1.get())
        arounds = [get_nums(each) for each in re.split(r';|；',self.entry2.get())]
        for i, center in enumerate(centers):
            self.program.log_window_text.insert('end', f'{center + 1}:\n')  # 提示原子序号
            bond_levels = self.caculater.get_atom_bond_levels(center, arounds[i])
            self.program.log_window_text.insert('end', f'键级和:{np.sum(bond_levels)}\n')
            base_level=self.program.config['base_level']
            self.program.log_window_text.insert('end', f'自由价:{base_level-np.sum(bond_levels)}\n')
            self.program.update_progress('计算自由价',(i+1)/len(centers))
