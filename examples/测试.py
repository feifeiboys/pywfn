
from multiprocessing import  Process
 
class MyProcess(Process): #继承Process类
    def __init__(self,name):
        super(MyProcess,self).__init__()
        self.name = name
        self.idx:int=None
 
    def run(self):
        print('测试多进程' , self.name , self.idx)
 
 
if __name__ == '__main__':
    process_list = []
    for i in range(5):  #开启5个子进程执行fun1函数
        p = MyProcess('Python') #实例化进程对象
        p.idx=i
        p.start()
        process_list.append(p)
 
    for i in process_list:
        p.join()
    print('执行完毕')