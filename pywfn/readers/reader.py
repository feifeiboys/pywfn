class Reader:
    """所有文件读取器的基类"""
    def __init__(self,path) -> None:
        self.path=path