import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
from ..utils import get_nums
from .script import Render
class Page:
    def __init__(self,program) -> None:
        self.program=program
        self.window = tk.Toplevel()
        pageWidth,pageHeight=self.program.config['pageWidth'],self.program.config['pageHeight']
        screenWidth,screenHeight=self.window.winfo_screenwidth(),self.window.winfo_screenheight()
        self.window.geometry(f'{pageWidth}x{pageHeight}+{int(screenWidth/2)}+{int(screenHeight/2-pageHeight/2)}')
        self.window.title(f'render point cloud:{os.path.basename(program.log_path)}')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.Render=Render(program)
    def init_variable(self):  # 定义tkinter变量
        pass

    def init_component(self): # 定义tkinter组件
        tk.Label(self.window, text='Enter atom number, split with , and -:').place(x=0, y=100, anchor='nw')
        self.entry1 = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='Enter obtial number, split with , and -:').place(x=0, y=200, anchor='w')
        self.entry2 = tk.Entry(self.window, show=None, width=200)
        self.caculate_button = ttk.Button(self.window, text='render', command=lambda:threading.Thread(target=self.render).start(),bootstyle=(SECONDARY,OUTLINE))


    def set_conponent_pos(self): # 定义tkinter组件位置
        self.entry1.place(x=0, y=150, anchor='nw')
        self.entry2.place(x=0, y=250, anchor='nw')
        self.caculate_button.place(x=240, y=500, anchor='center')

    def run(self): # 运行页面
        self.window.mainloop()

    def render(self):
        atoms = get_nums(self.entry1.get())
        obtials= get_nums(self.entry2.get())
        print(atoms,obtials)
        self.Render.render(atoms,obtials)