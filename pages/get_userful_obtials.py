import tkinter as tk
import matplotlib.pyplot as plt
import threading
import numpy as np
class Page():
    def __init__(self, program):
        self.main_program = program
        self.window = tk.Tk()
        self.window.geometry('480x640')
        self.window.title('获取有用轨道')
        self.init_variable()
        self.init_component()
        self.set_conponent_pos()
        self.caculater = self.main_program.caculater
        self.writer = self.main_program.writer

    def init_variable(self):
        self.if_save = tk.IntVar()

    def init_component(self):
        tk.Label(self.window, text='输入中心原子编号').place(x=0, y=100, anchor='nw')
        self.entry1 = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入周围原子编号，用,和-分割:').place(x=0, y=200, anchor='w')
        self.get_connection_button = tk.Button(self.window, text='自动获取', command=self.get_connection)
        self.entry2 = tk.Entry(self.window, show=None, width=200)
        tk.Label(self.window, text='输入需要判断的轨道编号，用,和-分割:').place(x=0, y=300, anchor='nw')
        self.entry3 = tk.Entry(self.window, show=None, width=200)
        self.caculate_button = tk.Button(self.window, text='计算有用轨道', command=self.caculate_tread)

    def set_conponent_pos(self):
        self.entry1.place(x=0, y=150, anchor='nw')
        self.get_connection_button.place(x=220, y=200, anchor='center')
        self.entry2.place(x=0, y=250, anchor='nw')
        self.entry3.place(x=0, y=350, anchor='nw')
        self.caculate_button.place(x=240, y=500, anchor='center')

    def run(self):
        self.window.mainloop()

    def num2str(self, nums):
        for i in range(len(nums)): nums[i] = str(nums[i])
        return nums

    def get_connection(self):
        connections = []
        center_atom_indexs = self.main_program.get_nums(self.entry1.get())
        for center_atom_index in center_atom_indexs:
            res = self.caculater.get_connections(center_atom_index)
            connections.append(res)
        # 在信息框输入
        self.entry2.delete(0, 'end')
        self.entry2.insert(0, ';'.join([','.join([str(i + 1) for i in each]) for each in connections]))

    def caculate_tread(self):
        t = threading.Thread(target=self.caculate)
        t.setDaemon(True)
        t.start()

    def caculate(self):  # 获取用户输入的参数
        center_atom_indexs = self.main_program.get_nums(self.entry1.get())
        around_atoms_indexs = [self.main_program.get_nums(each) for each in self.entry2.get().split(';')]
        obtial_indexs = self.main_program.get_nums(self.entry3.get())
        obtial_length = self.caculater.atoms[0]['datas'].shape[1]
        obtial_type = self.caculater.obtial_type
        if obtial_type == 1:
            obtial_indexs += [int(i+obtial_length/2) for i in obtial_indexs[:-1]]
        for i, center_atom_index in enumerate(center_atom_indexs):
            self.main_program.log_window_text.insert('end', f'{center_atom_index + 1}:\n')  # 提示原子序号
            bond_levels = self.caculater.get_atom_bond_levels(center_atom_index, around_atoms_indexs[i],obtial_indexs)
            self.main_program.log_window_text.insert('end', f'SUM:{np.sum(bond_levels)}\n')

