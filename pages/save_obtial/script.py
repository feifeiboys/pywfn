from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
from xlsxwriter import Workbook
import numpy as np

class Writer:
    def __init__(self,program) -> None:
        self.program=program
        #print(self.program.data)
    def save(self,atoms,obtials): #保存文件
        
        path=self.program.log_path
        self.file_path = asksaveasfilename(defaultextension='.xlsx', title='保存文件',initialfile=os.path.splitext(os.path.basename(path))[0])
        self.atoms=[i-1 for i in atoms]
        self.obtials=[i-1 for i in obtials]
        data=self.program.data # 主程序读取到的数据
        type_data=[
            {'key':'Molecular Orbital Coefficients','sheet_name':'coefficient'},
            {'key':'Alpha Molecular Orbital Coefficients','sheet_name':'coefficient_alpha'},
            {'key':'Beta Molecular Orbital Coefficients','sheet_name':'coefficient_beta'},
        ]
        for each in type_data:
            if each['key'] in data.keys():
                self.save_atom_obtials(sheet_name=each['sheet_name'],title=each['key'])
        

    # 保存原子轨道
    def save_atom_obtials(self, sheet_name,title):  # 保存所有或者选定的原子轨道
        self.wb=Workbook({'nan_inf_to_errors': True})
        atoms=self.atoms
        obtials=self.obtials
        all_obtials = self.program.data[title]  # 是一个列表，每个原子的轨道数据
        sheet = self.wb.add_worksheet(sheet_name)
        line_num = 0
        # 先在最上面写入选择的轨道

        sheet.write_row(line_num, 2, (np.array(obtials) + 1).tolist())
        line_num += 1
        for atom in atoms:
            each = all_obtials[atom]
            atom_type = each['atom_type']
            atom_id = each['atom_id']

            sheet.write(line_num, 0, f'{atom_id}{atom_type}')  # 写入原子编号
            sheet.write_row(line_num, 2, each['obtials'][:len(obtials)])  # 写入该原子的所有轨道类型
            line_num += 1
            index = each['datas'].index.tolist()
            sheet.write_column(line_num, 1, index)  # 写入原子轨道分量的列

            for idx in index:
                sheet.write_row(line_num, 2, each['datas'].loc[idx].iloc[obtials].to_list())
                line_num += 1
        self.wb.close()
        self.program.log_window_text.insert('end', '文件保存成功\n')