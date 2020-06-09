# -*- coding: utf-8 -*-
import sys
import time, datetime

sys.path.append(".")

'''
    针对流程化调用的装饰类，实现流程控制
'''
class Flower(object):
    '''
    测试流
        [
            {
                "case": object,    # 测试用例
                "pri":  0,         # 优先级
                "count": 1         # 调用次数, default = 1
                "result": object   # 测试结果
            }
        ]
    '''
    _flow = []

    def __init__(self, *dargs, **dkargs):
        self._dargs = dargs
        self._dkargs = dkargs
        # print("decrator param:", dargs, dkargs)

    def __call__(self, func):
        self._func = func
        def call_realfunc(*args, **kargs):
            # print("function param:", args, kargs)
            self.__addFlow(func, self._dkargs.get("pri"), self._dkargs.get("count"), *args, **kargs)
            # if self._dkargs.get("count") and self._dkargs.get("count") > 1:
            #     for i in range(self._dkargs.get("count")):
            #         self._func(*args, **kargs)
            # else:
            #     self._func(*args, **kargs)
        return call_realfunc
    
    # 添加测试用例
    def __addFlow(self, obj, pri, count, *args, **kargs):
        self._flow.append({
            "case" : obj,
            "args" : args,
            "kargs": kargs,
            "pri" : pri,
            "count" : count or 1,
            "result": []
        })

    # 添加测试用例
    def addFlow(obj, pri, count, *args, **kargs):
        self.__addFlow(obj, pri, count, *args, **kargs)

    @classmethod
    def run(cls):
        flow = cls._flow
        if len(flow) > 0:
            for _f in flow:
                for i in range(_f["count"]):
                    # 开始时间戳
                    start = int(round(time.time() * 1000000))
                    # 执行测试用例
                    res = _f["case"](*_f["args"], **_f["kargs"])
                    # 终止时间戳
                    end =  int(round(time.time() * 1000000))
                    interval = end - start
                    _f["result"].append(
                        {
                            "start_time": start,
                            "res": res,
                            "end_time": end,
                            "interval": interval,
                        }
                    )
        else:
            print("empty test case")

@Flower(group = "test", pri = 1, count = 3)
def test_flow():
    print("test_flow")

@Flower(1, group = "test", pri = 2, count = 3)
def test_flow2(a, b):
    print("test_flow2", a, b)

if __name__ == '__main__':
    test_flow()
    test_flow2("1", "2")
    Flower.run()
    print("over")