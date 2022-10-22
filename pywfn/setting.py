# 用来管理程序的一些设置
from pathlib import Path
BOND_LIMIT=1.7 # 判断量原子之间是否成键的长度限制
DEBUG=True # 是否开启debug,控制项目中所有的打印,避免与shell中的print冲突
GIF_TEMPLATE_PATH=Path(__file__).parent/'data/gifTemplate.txt' #批量导出gif文件时的模板文件