from .data import Elements
elements=Elements()


from . import setting

# print('pywfn 初始化',__name__)
def runShell():
    from .shell import Shell
    shell=Shell()
    shell.home()

from colorama import Fore,init
init(autoreset=True)
class Printer:
    def __init__(self) -> None:
        self.ifDebug=setting.IF_DEBUG

    def __call__(self,text,end='\n'):
        if self.ifDebug:
            print(text,end=end)

    def warn(self,text):
        self.__call__(Fore.YELLOW+text)

    def info(self,text):
        self.__call__(Fore.BLUE+text)

    def wrong(self,text):
        self.__call__(Fore.RED+text)
    
    def res(self,text):
        self.__call__(Fore.GREEN+text)

printer=Printer()