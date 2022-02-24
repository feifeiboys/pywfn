# 本脚本用来书写日志
import datetime
import logging
class Loger():
    def __init__(self) -> None:
        start_time=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # 时:分:秒
        logging.basicConfig(
            filename=f'logs/{start_time}.txt',
            format='%(asctime)s - %(filename)s - %(funcName)s - %(messages)s',
            level=logging.INFO
        )
        self.logger=logging.getLogger(__name__)
        self.logger.info(f'{start_time}')
    
    def add(self,content):
        self.logger.info(content)