import time
import traceback
import threading

"""
2019-09-04
本来我觉得原生的线程池应该比较好，可是我发现
from concurrent.futures import ThreadPoolExecutor, wait 
该线程池控制线程启动的时候，并不精确，我本来只想一次只运行一个

2025-03-20
线程数控制十分精确
"""


class ThreadExecutor:
    __task = []
    __task_count = 0  # 任务数
    __running_count = 0  # 正在执行的线程数

    __max_workers = 1  # 最大执行数量
    __done_task = []
    __fail_task = []

    __main = None
    __start_time = 0
    __finish_time = 0

    def __init__(self, task: list, max_workers=1):
        self.__task = task
        self.__task_count = len(task)
        self.__max_workers = max_workers

    def __repr__(self):
        print('任务数', self.__task_count)
        print('完成数', len(self.__done_task))
        print('失败数', len(self.__fail_task))
        print('运行数', self.__running_count)
        return ''

    def __worker(self):
        self.__running_count += 1
        while True:
            try:
                parameter = self.__task.pop()
            except:
                self.__finish_time = time.time_ns()
                break

            try:
                if isinstance(parameter, dict):
                    self.__main(**parameter)
                elif isinstance(parameter, (list, tuple)):
                    self.__main(*parameter)
                else:
                    self.__main(parameter)
                self.__done_task.append(parameter)
            except Exception as e:
                traceback.print_exc()
                print(e)
                self.__fail_task.append(parameter)

        self.__running_count -= 1

    def run(self, mian: callable):
        self.__start_time = time.time_ns()
        self.__main = mian
        for _ in range(self.__max_workers):
            threading.Thread(target=self.__worker).start()

    def is_finish(self):
        return len(self.__done_task) + len(self.__fail_task) >= self.__task_count


if '__main__' == __name__:
    def f(_id):
        time.sleep(1)


    t = [_ for _ in range(30)]

    te = ThreadExecutor(t, 10)
    te.run(f)
    print(te.is_finish())
    time.sleep(1)
    print(te)
    time.sleep(3)
    print(te.is_finish())
    print(te)
