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
        self.calculate_button=ttk.Button(self.window,text='1. select',command=lambda:threading.Thread(target=self.calculate).start())


    def set_conponent_pos(self):
        self.entry1.place(x=0, y=150, anchor='nw')
        self.calculate_button.place(x=240,y=600,anchor='center')


    def run(self):
        self.window.mainloop()

    def num2str(self, nums):
        for i in range(len(nums)): nums[i] = str(nums[i])
        return nums



    def calculate(self):

        centers = get_nums(self.entry1.get())
        self.caculater.calculate(centers) # 获得挑选出的轨道，并将挑选出的轨道按照格式输出
