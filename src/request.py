# -*- coding: utf-8 -*-
__version__ = '0.1'
""" A simple test tool,Named Ptesting
This is Ptesting, Version 0.1
Copyright 2020 skybosi, https://github.com/skybosi/ptesting
"""

import argparse
import importlib
import sys
import re
import os
import math
import time
import json
from multiprocessing import Process
from threading import Thread
os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(args)


black_list = {
    "loader.py": 1,
    "loader.pyc": 1,
    "request.py": 1,
    "request.pyc": 1,
    "__init__.py": 1,
    "__init__.pyc": 1,
}

COPYLEFT = """\nA simple test tool, Named Ptesting
This is Ptesting, Version 0.1
Copyright 2020 skybosi, https://github.com/skybosi/ptesting
-----------------------------------------------------------
"""
TEST_START = COPYLEFT + '{}.{} is Testing ... {} \n{} ======START-PTESTING====== {}'
TEST_END = '{} =======END-PTESTING======= {}\n{}.{} is Tested, Use {} ms'

# 当前文件所在目录的绝对路径
cur_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
currpath = os.path.abspath('.')
parentpath = os.path.abspath('..')

file_tb = []


def _initPath(path):
    '''
        处理跨平台文件路径
    '''
    if os.sep == '\\':
        path = path.replace('/', '\\')
    elif os.sep == '/':
        path = path.replace('\\', '/')
    path_tb = path.split(os.sep)
    # 绝对路径
    if os.path.isabs(path):
        path = path
    elif '.' == path_tb[0]:
        path = currpath + os.sep + os.sep.join(path_tb[1:])
    elif '..' == path_tb[0]:
        path = parent_path + os.sep + os.sep.join(path_tb[1:])
    elif not path_tb[0].startswith(os.sep):
        path = currpath + os.sep + os.sep.join(path_tb)
    else:
        raise IOError("Invalid path: ", path)
    debug(cur_path, currpath, path, parent_path, parentpath)
    return path


def _loadModule(path, filename):
    '''
        加载python模块
    '''
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
            if not a_dict[i].__doc__:
                a_dict[i].__doc__ = ''' unit; '''  # + str(len(varnames))
            func = _analysisNotes(
                a_dict, a_dict[i].__doc__, i, a_dict[i], *varnames)
            module_info["_func"].append(func)
        else:
            module_info["_vars"].append({i: a_dict[i]})
    return module_info


def _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs):
    '''
        生成call function
        # unit test is a simple case COUNT type, just like c:1 n:1
        # def call_realfunc():
        #     start_time = int(round(time.time() * 1000))
        #     print(TEST_START.format(
        #         ctx['__name__'], funName, start_time, args_tb['type'], args_tb['type']))
        #     if 0 != args_tb['args_num']:
        #         dargs = args_tb['args'][:args_tb['args_num']]
        #         func(*dargs, **dkargs)
        #     else:
        #         func()
        #     end_time = int(round(time.time() * 1000))
        #     print(TEST_END.format(
        #         args_tb['type'], args_tb['type'], ctx['__name__'], funName, end_time - start_time))
        # return call_realfunc
    '''
    def call_realfunc():
        start_time = int(round(time.time() * 1000))
        print(TEST_START.format(ctx['__name__'],
                                funName, start_time, args_tb['desc'], args_tb['desc']))
        lis = []
        for _ in range(args_tb['c']):
            # p = Process(target=task1)
            def Loop(n, *dargs, **dkargs):
                dargs = args_tb['args']
                emptyArgs = True
                if 0 != args_tb['args_num']:
                    emptyArgs = False
                    dargs = args_tb['args'][:args_tb['args_num']]
                for _ in range(n):
                    if not emptyArgs:
                        ctx[funName]['cb'] = func(*dargs, **dkargs)
                    else:
                        ctx[funName]['cb'] = func()
            t = Thread(target=Loop, args=[args_tb['npc'], *dargs])
            lis.append(t)
            t.start()
        for t in lis:
            t.join()
        end_time = int(round(time.time() * 1000))
        print(TEST_END.format(
            args_tb['desc'], args_tb['desc'], ctx['__name__'], funName, end_time - start_time))
    return call_realfunc


def _analysisNotes(ctx, input, funName, func, *dargs, **dkargs):
    '''
        分析注释
    '''
    if type(input) != type("") or 0 == len(input):
        return None
    # 3.清除 // 行级注释
    input = re.sub('\'', '"', re.sub(
        r'\s+', "", re.sub(r'[//|#].*', '', input)))
    if type(input) != type("") or 0 == len(input):
        return None
    args_tb = {}
    try:  # json 类型
        args_tb = json.loads(input)
        args_tb['type'] = args_tb['type'].upper()
        args_tb['args_num'] = len(dargs)
        args_tb['npc'] = math.floor(
            args_tb['n'] / args_tb['c'])  # 每个独立线程中执行的次数
        debug(args_tb)
    except:  # csv 类型
        input_tb = input.split(';')
        input_tb = list(map(lambda x: x.strip(), input_tb))
        args_tb['type'] = input_tb[0].upper()
        args_tb['args_num'] = len(dargs)
        if 'UNIT' == args_tb['type']:
            input_tb = input_tb[1].split(',')
            input_tb = list(map(lambda x: x.strip(), input_tb))
            args_tb['args'] = input_tb
            args_tb['c'] = 1
            args_tb['n'] = 1
            args_tb['npc'] = 1
            # 必须参数检测
            if args_tb['args_num'] > len(args_tb['args']):
                raise TypeError("Unit Testing: " + funName + ": Must " + str(args_tb['args_num']) +
                                " Args, But Get " + str(len(args_tb['args'])))
        elif 'COUNT' == args_tb['type']:
            input_tb = input_tb[1].split(',')
            input_tb = list(map(lambda x: x.strip(), input_tb))
            args_tb['c'] = int(input_tb[0])  # 并发数
            args_tb['n'] = int(input_tb[1])  # 并发请求的总数
            args_tb['npc'] = math.floor(
                args_tb['n'] / args_tb['c'])  # 每个独立线程中执行的次数
            args_tb['args'] = input_tb[2:]
            # 必须参数检测
            if args_tb['args_num'] > len(args_tb['args']):
                raise TypeError("Count Testing: " + funName + ": Must " + str(args_tb['args_num']) +
                                " Args, But Get " + str(len(args_tb['args'])))
        elif 'FLOW' == args_tb['type']:
            input_tb = input_tb[1].split(',')
            input_tb = list(map(lambda x: x.strip(), input_tb))
            args_tb['args'] = input_tb[1:]
            srt_tb = input_tb[0].split('-')
            srt_tb = list(map(lambda x: x.strip(), srt_tb))
            args_tb['s'] = srt_tb[0]  # step
            step_pos = args_tb['s'].find(':')
            if step_pos > 0:
                args_tb['sn'] = args_tb['s'][:step_pos]
                args_tb['s'] = int(args_tb['s'][step_pos+1:])
            else:
                args_tb['sn'] = 'flow_step' + args_tb['s']
                args_tb['s'] = int(args_tb['s'])
            if len(srt_tb) > 2:  # 定义重试机制
                if len(srt_tb) == 4:  # 定义并发情况
                    args_tb['c'] = int(srt_tb[1])  # 并发数
                    args_tb['n'] = int(srt_tb[2])  # 并发请求的总数
                    args_tb['npc'] = math.floor(
                        args_tb['n'] / args_tb['c'])  # 每个独立线程中执行的次数
                elif len(srt_tb) == 3:  # 默认并发数1
                    args_tb['c'] = 1               # 并发数
                    args_tb['n'] = int(srt_tb[1])  # 并发请求的总数
                    args_tb['npc'] = args_tb['n']  # 每个独立线程中执行的次数
            else:
                args_tb['c'] = 1               # 并发数
                args_tb['n'] = int(srt_tb[1])  # 并发请求的总数
                args_tb['npc'] = args_tb['n']  # 每个独立线程中执行的次数
            args_tb['t'] = int(srt_tb[-1])            # total
            # 必须参数检测
            if args_tb['args_num'] > len(args_tb['args']):
                raise TypeError("Count Testing: " + funName + ": Must " + str(args_tb['args_num']) +
                                " Args, But Get " + str(len(args_tb['args'])))
            debug(args_tb)
    finally:
        pass
    ctx[funName] = {}
    args_tb['desc'] = args_tb['type'] + ":" + \
        str(args_tb['c']) + "-" + str(args_tb['n'])
    # 单元测试
    if 'UNIT' == args_tb['type']:
        args_tb['desc'] = args_tb['type']
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs)
    # 并发测试
    elif 'COUNT' == args_tb['type']:
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs)
    # 流程测试
    elif 'FLOW' == args_tb['type']:
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs)
    else:
        raise TypeError("Unkonw Testing Type: " + funName)


def _parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(description='A simple test tool')
    parser.add_argument('-p', '--path', type=str, required=False, default="./",
                        help='test case path')
    parser.add_argument('-l', '--level', type=int, required=False, default=-1,
                        help='load module dir level')
    parser.add_argument('-t', '--type', type=str, required=False, default='a',
                        help='only test a type case: a:all u:unit c:count f:flow')
    return parser.parse_args()


def loading(path, level, cur):
    '''
        加载某一路径的所有python
        实现动态加载py
        @path: 待加载的路径，支持相对路径，绝对路径
    '''
    cur = cur + 1
    if level > 0 and cur > level:
        return None
    path = _initPath(path)
    # 获取目录下的文件与目录列表
    try:
        pathList = os.listdir(path)
    except IOError:
        raise IOError("Invalid path: ", path)
    finally:
        os.sys.path.append(path)
        debug(os.sys.path)
    # 遍历列表中的文件名
    for filename in pathList:
        absPath = os.path.join(path, filename)
        # 通过绝对路径判断是否是文件
        if os.path.isfile(absPath):
            module_info = _loadModule(path, filename)
            if module_info:
                file_tb.append(module_info)
        else:
            if not filename.startswith('.') and not filename.startswith('__'):
                loading(absPath, level, cur)
    return file_tb


if __name__ == '__main__':
    args = _parse_args()
    try:
        lib_tb = loading(args.path, args.level, 0)
        # debug(lib_tb)
        for lib in lib_tb:
            for i in lib["_func"]:
                i()
    except Exception as e:
        print("Load module from {} failed ...: {}".format(args.path, e))
