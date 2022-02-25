import numpy as np
import pandas as pd
import math
import sympy
import matplotlib.pyplot as plt

class Caculater:
    def __init__(self, program):
        self.program = program
        self.logger=program.logger
        self.obtial_type = None # 轨道类型，是否为劈裂
        self.atoms_pos = None
        self.atoms = None
        self.standard_basis = None
        self.PX = '2PX'
        self.PY = '2PY'
        self.PZ = '2PZ'
        self.set_data()

    def set_data(self):
        data=self.program.data
        keys = data.keys()
        if 'Standard orientation' in keys:
            self.atoms_pos = data['Standard orientation']
        # 轨道类型有两种情况，正常的和劈裂为α、β的
        if 'Molecular Orbital Coefficients' in keys:
            self.obtial_type = 0
            self.atoms = data['Molecular Orbital Coefficients'] # [O,O,O,V,V,V]
            obtial_num = data['Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{obtial_num}个轨道\n')
        elif ('Alpha Molecular Orbital Coefficients' in keys) and ('Beta Molecular Orbital Coefficients' in keys):
            self.alpha_num = data['Alpha Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.beta_num = data['Beta Molecular Orbital Coefficients'][0]['datas'].shape[1]
            self.program.log_window_text.insert('end',f'读取到{self.alpha_num}个Alpha轨道和{self.beta_num}个Beta轨道\n')
            self.obtial_type = 1
            self.atoms = [{
                'atom_id': alpha['atom_id'],
                'atom_type': alpha['atom_type'],
                'datas': pd.concat([alpha['datas'], beta['datas']], axis=1), # 将α和β的轨道数据横向拼接在一起[O,O,O,V,V,V,O,O,O,V,V,V]
                'obtials': alpha['obtials'] + beta['obtials']
            } for alpha, beta in
                zip(data['Alpha Molecular Orbital Coefficients'], data['Beta Molecular Orbital Coefficients'])]
        self.obtials=self.atoms[0]['datas'].columns # 所有的轨道类型(占据或非占据，可能会有复杂的表示)
        print(self.obtials)
        self.obtial_length = self.atoms[0]['datas'].shape[1] # 轨道的数量
        if 'Standard basis' in data.keys():
            self.standard_basis = data['Standard basis']

    def get_p_obtial(self,atom,obtial):  # 返回指定原子的pz,py和pz轨道
        atoms = self.atoms
        px = atoms[atom]['datas'].loc[self.PX].iloc[obtial]
        py = atoms[atom]['datas'].loc[self.PY].iloc[obtial]
        pz = atoms[atom]['datas'].loc[self.PZ].iloc[obtial]
        return np.array([px, py, pz], dtype=np.float64)

    def function(self, center_pos, pos, alpha, cs, Ps):  # 获取函数值 (原子坐标，计算点坐标，alpha，c，轨道系数,函数平移)
        xn, yn, zn = center_pos
        xi, yi, zi = pos
        PX, PY, PZ = Ps
        pi = math.pi
        e = math.e
        a = sympy.symbols('alpha')
        N = (2 * a / pi) ** (3 / 4) * 2 * a ** 0.5
        r = (xi - xn) ** 2 + (yi - yn) ** 2 + (zi - zn) ** 2
        fx = N * (xi - xn) * e ** (-a * r)
        fy = N * (yi - yn) * e ** (-a * r)
        fz = N * (zi - zn) * e ** (-a * r)
        fpx = sum([c * fx.subs(a, a_) for c, a_ in zip(cs, alpha)])
        fpy = sum([c * fy.subs(a, a_) for c, a_ in zip(cs, alpha)])
        fpz = sum([c * fz.subs(a, a_) for c, a_ in zip(cs, alpha)])
        f = PX * fpx + PY * fpy + PZ * fpz
        return f

    def get_px(self, atom, obtial):
        px,py,pz=self.get_p_obtial(atom,obtial)
        center_unit_matrix = self.get_unit_matrix([atom])
        all_square_sum = self.get_all_atom_square_sum()
        PX = (px ** 2 / all_square_sum[atom]) ** 0.5 * center_unit_matrix[0].flatten()[obtial]
        PY = (py ** 2 / all_square_sum[atom]) ** 0.5 * center_unit_matrix[1].flatten()[obtial]
        PZ = (pz ** 2 / all_square_sum[atom]) ** 0.5 * center_unit_matrix[2].flatten()[obtial]
        return PX, PY, PZ

    # 判断两个原子之间的轨道是不是π轨道,(中心原子序号，周围原子序号，轨道序号)
    def get_obtial_is_userful(self, center, around, obtial):  # 这里传入的应当是用户输入的
        atoms = self.atoms
        all_square_sum = self.get_all_atom_square_sum()[obtial]
        center_datas = atoms[center]['datas']
        px = center_datas.loc[self.PX][obtial]  # 从log文件中提取的轨道系数
        py = center_datas.loc[self.PY][obtial]
        pz = center_datas.loc[self.PZ][obtial]
        p_sums_center = px ** 2 / all_square_sum + py ** 2 / all_square_sum + pz ** 2 / all_square_sum

        around_datas = atoms[around]['datas']
        px = around_datas.loc[self.PX].astype('float').to_numpy()[obtial]  # 从log文件中提取的轨道系数
        py = around_datas.loc[self.PY].astype('float').to_numpy()[obtial]
        pz = around_datas.loc[self.PZ].astype('float').to_numpy()[obtial]
        p_sums_around = px ** 2 / all_square_sum + py ** 2 / all_square_sum + pz ** 2 / all_square_sum
        # 针对通用体系想出来的方法
        self.logger.info(f'center:{center+1},around:{around+1},obtial:{obtial+1}')
        self.logger.info(f'p_sum_center:{p_sums_center},p_sum_around:{p_sums_around}')
        if p_sums_center < 0.008 and p_sums_around < 0.008:
            
            return False
        
        if center != around and atoms[around]['atom_type'] != 'H':
            # 分别获取与中心原子和周围原子相连的原子
            all_res=[]
            center_connections=self.get_connections(center)
            around_connections=self.get_connections(around)
            for each in center_connections:
                if atoms[each]['atom_type']!='H':
                    res=np.max(np.abs(self.get_cloud(center,each,obtial)))
                    all_res.append(res)
            for each in around_connections:
                if atoms[each]['atom_type']!='H':
                    res=np.max(np.abs(self.get_cloud(around,each,obtial)))
                    all_res.append(res)
            result=max(all_res)
            self.logger.info(f'result:{result}')
            if result < 0.01:
                return True
            else:
                return False

    def get_cloud(self,center, around, obtial):  # 获取中心原子和周围原子之间十个点的函数值
        x = self.atoms_pos.iloc[center].loc['X']
        y = self.atoms_pos.iloc[center].loc['Y']
        z = self.atoms_pos.iloc[center].loc['Z']
        paras = np.array(self.standard_basis[center])
        all_square_sum = self.get_all_atom_square_sum()[obtial]
        px = self.atoms[center]['datas'].loc[self.PX].astype('float').to_numpy()[obtial]  # 从log文件中提取的轨道系数
        py = self.atoms[center]['datas'].loc[self.PY].astype('float').to_numpy()[obtial]
        pz = self.atoms[center]['datas'].loc[self.PZ].astype('float').to_numpy()[obtial]
        center_unit_matrix = self.get_unit_matrix([center])
        PX = (px ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[0].flatten()[obtial]
        PY = (py ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[1].flatten()[obtial]
        PZ = (pz ** 2 / all_square_sum) ** 0.5 * center_unit_matrix[2].flatten()[obtial]
        x_ = self.atoms_pos.iloc[around].loc['X']
        y_ = self.atoms_pos.iloc[around].loc['Y']
        z_ = self.atoms_pos.iloc[around].loc['Z']
        dx = (x_ - x)
        dy = (y_ - y)
        dz = (z_ - z)
        results = []
        num = 10
        for i,x in enumerate(np.arange(0, 1, 1/num)):
            res = self.function(center_pos=(x, y, z), pos=(x + dx / num * i, y + dy / num * i, z + dz / num * i),
                                alpha=paras[:, 0].tolist(), cs=paras[:, 1].tolist(), Ps=(PX, PY, PZ))
            results.append(res)
        return results


    def obtial_between_atoms(self, center, around):  # 挑选两个原子之间π键有哪些
        userful = []
        obtial_num = self.obtial_length
        for obtial in range(obtial_num):  # 所有的O轨道都判断
            # 如果当前轨道不是占据轨道则直接跳过
            if self.obtials[obtial][-1]!='O':
                continue
            if self.obtial_type == 0:
                res = self.get_obtial_is_userful(center, around,obtial)
                if res:
                    userful.append(obtial)
            if self.obtial_type == 1:
                res = self.get_obtial_is_userful(center,around,obtial)
                if res:
                    userful.append(obtial)
        return userful

    def get_connections(self, atom):  # 计算所有原子与指定原子之间的距离,进而判断与之相连的原子
        atoms_pos = self.atoms_pos
        dxs = atoms_pos.loc[:, 'X'] - atoms_pos.iloc[atom].loc['X']
        dys = atoms_pos.loc[:, 'Y'] - atoms_pos.iloc[atom].loc['Y']
        dzs = atoms_pos.loc[:, 'Z'] - atoms_pos.iloc[atom].loc['Z']
        distances = (dxs ** 2 + dys ** 2 + dzs ** 2) ** 0.5
        res = np.where(distances < 2)[0].tolist()
        res.remove(atom)
        return res

    def get_each_atom_square_sum(self, select_atoms):  # 获取每一个原子的所有轨道的平方和
        atoms = self.atoms
        square_sums = []
        for i in select_atoms:
            atom = atoms[i]
            square_sums.append(np.sum(atom['datas'].astype('float').to_numpy() ** 2, axis=0)[np.newaxis, :])
        res = np.concatenate(square_sums, axis=0)
        return res

    def get_all_atom_square_sum(self):  # 获取所有原子轨道平方和
        res = np.concatenate([atom['datas'].astype('float').to_numpy() ** 2 for atom in self.atoms]).sum(axis=0)
        return res

    def get_unit_matrix(self, select_atoms):  # 根据每个原子的2PX,2PY,2PZ轨道的正负获取单位矩阵,跑的通的代码尽量不要改>_<
        px_list = []
        py_list = []
        pz_list = []
        atoms = self.atoms
        for i in select_atoms:
            atom = atoms[i]
            px_list.append(atom['datas'].loc[self.PX].astype('float').to_numpy()[np.newaxis, :])  # 添加新轴
            py_list.append(atom['datas'].loc[self.PY].astype('float').to_numpy()[np.newaxis, :])
            pz_list.append(atom['datas'].loc[self.PZ].astype('float').to_numpy()[np.newaxis, :])
        px_res = np.concatenate(px_list, axis=0)
        px_res[px_res > 0] = 1
        px_res[px_res < 0] = -1
        py_res = np.concatenate(py_list, axis=0)
        py_res[py_res > 0] = 1
        py_res[py_res < 0] = -1
        pz_res = np.concatenate(pz_list, axis=0)
        pz_res[pz_res > 0] = 1
        pz_res[pz_res < 0] = -1
        return np.array([px_res, py_res, pz_res])  # 返回某个原子的所有轨道的2px,2py,2pz

    def get_unit(self, center, around, obtial):  # 判断两原子之间的正负关系
        res=np.sum(self.get_p_obtial(center,obtial)*self.get_p_obtial(around,obtial))
        return 1 if res > 0 else -1

    def get_bond_level_between_tow_atom(self, center, around,input_obtials=None):  # 计算两个原子之间的键级
        if input_obtials is None:
            userful_obtials = self.obtial_between_atoms(center,around)
        else:
            userful_obtials = input_obtials
        around_units = [self.get_unit(center, around, obtial) for obtial in userful_obtials] # 周围原子与中心原子之间的正负系数
        around_units = np.array(around_units).reshape(1, len(userful_obtials))
        center_units = np.ones((1, len(userful_obtials)))

        if self.obtial_type == 0:
            userful_str = [str(i+1) for i in userful_obtials]
            self.program.log_window_text.insert('end',f'{center+1}->{around+1}π轨道：'+','.join(userful_str)+'\n')
        else:
            userful_str = [f'α{i+1}' if i < self.alpha_num else f'β{i+1-self.alpha_num}' for i in userful_obtials]
            self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},π轨道：' + ','.join(userful_str) + '\n')
        all_square_sum = self.get_all_atom_square_sum()[np.newaxis, :][:, userful_obtials]
        center_square_sum = self.get_each_atom_square_sum([center])[:, userful_obtials]
        around_square_sum = self.get_each_atom_square_sum([around])[:, userful_obtials]
        center_res = (center_square_sum / all_square_sum) ** 0.5 * center_units
        around_res = (around_square_sum / all_square_sum) ** 0.5 * around_units
        bond_level = np.sum((2 if self.obtial_type == 0 else 1) * center_res * around_res)
        return bond_level

    def get_atom_bond_levels(self, center, arounds,all_obtials):  # 计算某个原子与周围原子之间的键级
        bond_levels = []
        i=0
        for around in arounds:
            if self.atoms[around]['atom_type'] != 'H':
                bond_level = self.get_bond_level_between_tow_atom(center, around,None if len(all_obtials)==0 else all_obtials[i])
                i+=1
                bond_levels.append(bond_level)
                self.program.log_window_text.insert('end', f'{center + 1}->{around + 1},键级:{bond_level}\n')
        return np.array(bond_levels)
    