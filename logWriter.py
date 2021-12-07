# 此脚本用来保存读取和计算到的结果
from xlsxwriter import Workbook
import numpy as np


class Writer:
    def __init__(self, program):
        self.wb = Workbook({'nan_inf_to_errors': True})
        self.program = program
        self.data = None

    # 保存原子轨道
    def save_atom_obtials(self, sheet_name,title, **kw):  # 保存所有或者选定的原子轨道
        obtials = self.data[title]
        if 'select_obtials' in kw.keys():
            select_obtials = kw['select_obtials']
        else:
            select_obtials = obtials[0]['datas'].columns.to_numpy().tolist()  # 所有的轨道
        if 'select_atoms' in kw.keys():
            select_atoms = kw['select_atoms']
        else:
            select_atoms = list(range(len(obtials)))
        sheet = self.wb.add_worksheet(sheet_name)
        line_num = 0
        # 先在最上面写入选择的轨道

        sheet.write_row(line_num, 2, (np.array(select_obtials) + 1).tolist())
        line_num += 1
        for select_atom in select_atoms:
            each = obtials[select_atom]
            atom_type = each['atom_type']
            atom_id = each['atom_id']

            sheet.write(line_num, 0, f'{atom_id}{atom_type}')  # 写入原子编号
            sheet.write_row(line_num, 2, each['obtials'][:len(select_obtials)])  # 写入该原子的所有轨道类型
            line_num += 1
            index = each['datas'].index.tolist()
            sheet.write_column(line_num, 1, index)  # 写入原子轨道分量的列
            obtials_frame = each['datas'][select_obtials].astype('float').to_numpy()
            for obtial in obtials_frame:
                sheet.write_row(line_num, 2, obtial.tolist())
                line_num += 1

    def save_userful_obtial(self, all_userful):
        sheet = self.wb.add_worksheet('userful_obtials')
        for i, each in enumerate(all_userful):
            sheet.write_row(i, 0, each)

    def save(self, file_path):
        self.wb.filename = file_path
        self.wb.close()
