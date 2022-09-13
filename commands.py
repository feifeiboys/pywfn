"""处理用户在文本框输入的文本"""

class Command:
    def __init__(self,app:"Window") -> None:
        self.app:Window=app
        self.currentFile:"FileItem"


    def printf(self,txt:str):
        return txt


    def run(self,opt:str):
        self.currentFile=self.app.currentFile
        try:
            res=eval(f'self.{opt}')
            return res
        except:
            return 'command error'


from App import Window,FileItem