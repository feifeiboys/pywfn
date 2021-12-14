import tkinter as tk
import matplotlib.pyplot as plt
import threading
import numpy as np


class Page:
    def __init__(self, program):
        self.program = program
        self.window = tk.Tk()
        self.window.geometry('400x640')
        self.window.title('计算键轴函数值')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.caculater = self.program.caculater
        self.writer = self.program.writer

    def init_variable(self):
        self.if_save = tk.IntVar()

    def init_component(self):
        tk.Label(self.window, text='输入中心原子编号').place(x=0, y=100, anchor='w')
        self.entry_center = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入周围原子编号').place(x=0, y=200, anchor='w')
        self.entry_around = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入轨道序号').place(x=0, y=300, anchor='w')
        self.entry_obtial = tk.Entry(self.window, show=None, width=200)
        self.caculate_button = tk.Button(self.window, text='计算键轴上函数值', command=self.get_cloud)

    def set_conponent_pos(self):
        self.entry_center.place(x=0, y=150, anchor='nw')
        self.entry_around.place(x=0, y=250, anchor='nw')
        self.entry_obtial.place(x=0, y=350, anchor='nw')
        self.caculate_button.place(x=200, y=500, anchor='center')

    def run(self):
        self.window.mainloop()

    def get_cloud(self):
        center=int(self.entry_center.get())-1
        around = int(self.entry_around.get()) - 1
        obtial = int(self.entry_obtial.get()) - 1
        self.caculater.get_clouds(center,around,obtial)

