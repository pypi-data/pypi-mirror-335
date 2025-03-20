from collections import deque
import time
import random
import loguru
import sys

class DRRatePacer:
    def __init__(self, logger, verbose, stat_window):
        self.logger = logger
        self.verbose = verbose
        self.stat_window = stat_window
        self.history = deque(maxlen=stat_window)  # 维护最近 `stat_window` 个决策
        self.count = 0  # 记录当前已经处理的决策数
    
    def found_duplicated(self):
        # 记录重复项
        self.history.append(("duplicate", 1))
        self.count += 1
        if self.count >= self.stat_window:  # 如果收集的记录数已经达到 stat_window
            self.log_duplication_rate()
            self.count = 0

    def found_not_duplicate(self):
        # 记录非重复项
        self.history.append(("none", 0))
        self.count += 1
        if self.count >= self.stat_window:  # 如果收集的记录数已经达到 stat_window
            self.log_duplication_rate()
            self.count =  0

    def log_duplication_rate(self):
        """计算并记录重复率和类型占比"""
        if len(self.history) < self.stat_window:  # 防止除 0
            return
        
        total_count = len(self.history)
        duplicate_count = sum(1 for _, v in self.history if v == 1)

        duplication_rate = duplicate_count / total_count

        # 输出日志，包括当前窗口中的样本数量
        if self.logger: self.logger.info(f"<DRRateObserver> dynamic duplication rate (window: {self.stat_window}): {duplication_rate:.2f}, samples in window: {total_count}")

        # 重置计数器，防止重复日志
        self.count = 0

if __name__ == "__main__":
    logger = loguru.logger  # 初始化 loguru 日志记录器
    
    logger.remove()  
    logger.add(
        sys.stdout, 
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO"
    )
    logger.add(
        "feature_test.log",  # 输出到日志文件
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO",  
    )
    
    observer = DRRatePacer(logger,False, 1000)  # 维护最近 1000 次决策

    while True:
        # 模拟90%是重复项
        is_duplicate = random.random() < 0.9  
        
        if is_duplicate:
            observer.found_duplicated()
        else:
            observer.found_not_duplicate()

        # time.sleep(0.01)  # 每 0.01 秒更新一次
