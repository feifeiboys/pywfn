from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
from xlsxwriter import Workbook
import numpy as np

class Writer:
    def __init__(self) -> None:
        self.wb=Workbook({'nan_inf_to_errors': True})
    def save(self,atoms,obtials,data,path,program): #保存文件
        self.file_path = asksaveasfilename(defaultextension='.xlsx', title='保存文件',initialfile=os.path.splitext(os.path.basename(path)))[0]
        self.data=data
        self.atoms=atoms
        self.obtials=obtials
        if 'Molecular Orbital Coefficients' in data.keys():
            self.save_atom_obtials('coefficient', 'Molecular Orbital Coefficients')
        if 'Alpha Molecular Orbital Coefficients' in data.keys():
            self.save_atom_obtials('coefficient_alpha', 'Alpha Molecular Orbital Coefficients')
        if 'Beta Molecular Orbital Coefficients' in data.keys():
            self.save_atom_obtials('coefficient_beta', 'Beta Molecular Orbital Coefficients',
                                            atoms=atoms, obtials=obtials)
        program.log_window_text.insert('end', '文件保存成功\n')

    # 保存原子轨道
    def save_atom_obtials(self, sheet_name,title, obtials,atoms):  # 保存所有或者选定的原子轨道
        all_obtials = self.data[title]  # 是一个列表，每个原子的轨道数据
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