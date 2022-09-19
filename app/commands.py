"""处理用户在命令行文本框输入的命令"""

class Command:
    def __init__(self,app:"Window") -> None:
        self.app:Window=app
        self.currentFile:"FileItem"


    def printf(self,txt:str):
        return txt


    def run(self,opt:str):
        self.currentFile=self.app.currentFile
        printf=self.printf
        try:
            res=eval(f'{opt}')
            return res
        except:
            return 'command error'


# from .window import Window,FileItem