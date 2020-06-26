# -*- coding: utf-8 -*-
import importlib
import error
import sys
import re
import os
import math
import time
import os
from multiprocessing import Process
from threading import Thread

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(args)


'''
    加载某一路径的所有python
    实现动态加载py
'''

black_list = {
    "loader.py": 1,
    "loader.pyc": 1,
    "error.py": 1,
    "error.pyc": 1,
    "request.py": 1,
    "request.pyc": 1,
    "__init__.py": 1,
    "__init__.pyc": 1,
}

# 当前文件所在目录的绝对路径
cur_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
currpath = os.path.abspath('.')
parentpath = os.path.abspath('..')

file_tb = []

'''
    处理跨平台文件路径
'''


def initPath(path):
    if os.sep == '\\':
        path = path.replace('/', '\\')
    elif os.sep == '/':
        path = path.replace('\\', '/')
    path_tb = path.split(os.sep)
    # 绝对路径
    if os.path.isabs(path):
        path = path
    elif '.' == path_tb[0]:
        path = currpath + os.sep + path_tb[1]
    elif '..' == path_tb[0]:
        path = parent_path + os.sep + path_tb[1]
    elif len(path_tb) <= 1:
        path = currpath + os.sep + path_tb[0]
    else:
        path = currpath + os.sep + path_tb[1]
    # debug(cur_path, currpath, path, parent_path, parentpath)
    return path


'''
    加载python模块
'''


def loadModule(path, filename):
    # 使用join函数对路径进行拼接，然后构成绝对路径
    if black_list.get(filename) or not filename.endswith('.py') or filename.startswith('.'):
        return None
    if not os.path.exists(path + os.sep + '__init__.py'):
        fd = open(path + os.sep + '__init__.py', mode='w')
        fd.close()
    absPath = os.path.join(path, filename)
    relPath = os.path.relpath(absPath)
    module_tb = relPath.split(os.sep)
    # module_dir = module_tb[0]
    module_name = module_tb[-1].split('.')[0]
    module_path = '.'.join(module_tb[:-1]) + '.' + module_name
    debug("module_tb:", module_tb)
    a = importlib.import_module(module_name, module_path)
    debug(a)
    a_dict = a.__dict__
    module_info = {
        "_func": [],
        "_vars": [],
        "_clas": [],
        "_file": absPath,
        "_module": a
    }
    for i in a_dict:
        if i.startswith('__'):  # 非内置变量
            module_info[i] = a_dict[i]
        elif type(a_dict[i]) == type(object):  # 类
            module_info["_clas"].append({i: a_dict[i]})
        elif hasattr(a_dict[i], "__call__"):  # 函数
            func = a_dict[i]
            varnames = func.__code__.co_varnames
            if a_dict[i].__doc__:
                a_dict[i].__doc__ = ''' unit, ''' + str(varnames)
            func = analysisNotes(a_dict[i].__doc__, i, a_dict[i], *varnames)
            module_info["_func"].append(func)
        else:
            module_info["_vars"].append({i: a_dict[i]})
    return module_info


'''
    分析注释
'''


def analysisNotes(input, funName, func, *dargs, **dkargs):
    if type(input) != type("") or 0 == len(input):
        return None
    input_tb = input.split(',')
    input_tb = list(map(lambda x: x.strip(), input_tb))
    # 单元测试
    if 'unit' == input_tb[0].lower():
        inargs = input_tb[1:]
        # 必须参数检测
        if len(dargs) > len(inargs):
            raise TypeError("Unit Testing: " + funName + ": Must " + str(len(dargs)) +
                            " Args, But Get " + str(len(inargs)))

        def call_realfunc(*dargs, **dkargs):
            dargs = inargs
            func(*dargs, **dkargs)
        return call_realfunc
    # 并发测试
    elif 'count' == input_tb[0].lower():
        inargs = input_tb[3:]
        # 必须参数检测
        if len(dargs) > len(inargs):
            raise TypeError("Count Testing: " + funName + ": Must " + str(len(dargs)) +
                            " Args, But Get " + str(len(inargs)))

        def call_realfunc(*args, **kargs):
            start_time = time.time()
            lis = []
            for _ in range(int(input_tb[1])):
                # p = Process(target=task1)
                n = math.floor(int(input_tb[2]) / int(input_tb[1]))

                def Loop(n, *dargs, **dkargs):
                    i = 0
                    dargs = inargs
                    while i < n:
                        func(*dargs, **dkargs)
                        i = i + 1
                t = Thread(target=Loop, args=[n, *dargs], kwargs=dkargs)
                lis.append(t)
                t.start()
            for t in lis:
                t.join()
            end_time = time.time()
            debug('程序执行时间为', end_time - start_time)
        return call_realfunc
    # 流程测试
    elif 'flow' == input_tb[0].lower():
        pass
    else:
        raise TypeError("Unkonw Testing Type: " + funName)


'''
    加载某一个路径的所有模块
'''


def loading(path):
    path = initPath(path)
    # 获取目录下的文件与目录列表
    try:
        pathList = os.listdir(path)
    except IOError:
        return {}
    finally:
        os.sys.path.append(path)
        debug(os.sys.path)
    # 遍历列表中的文件名
    for filename in pathList:
        absPath = os.path.join(path, filename)
        # 通过绝对路径判断是否是文件
        if os.path.isfile(absPath):
            module_info = loadModule(path, filename)
            if module_info:
                file_tb.append(module_info)
        else:
            if not filename.startswith('.') and not filename.startswith('__'):
                loading(absPath)
    return file_tb


if __name__ == '__main__':
    file_tb = loading(sys.argv[1])
    print(file_tb)
