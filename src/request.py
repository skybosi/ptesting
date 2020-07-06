# -*- coding: utf-8 -*-
__version__ = '0.1'
__all__ = ["loading", "show"]
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
END_NOTE = """-----------------------------------------------------------
Congratulation! All Case is Tested At """

TEST_START = '{}.{} is Testing ... \n{} ======START-PTESTING====== {}'
TEST_END = '{} =======END-PTESTING======= {}\n{}.{} is Tested, Use {} ms\n'

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


def _loadModule(path, filename, cmd_args):
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
        "_module": a,
    }
    for i in a_dict:
        if i.startswith('__'):  # 非内置变量
            module_info[i] = a_dict[i]
        elif type(a_dict[i]) == type(object):  # 类
            module_info["_clas"].append({i: a_dict[i]})
        elif hasattr(a_dict[i], "__call__"):  # 函数
            func = a_dict[i]
            varnames = func.__code__.co_varnames
            argcount = func.__code__.co_argcount
            if not a_dict[i].__doc__:
                a_dict[i].__doc__ = ''' unit; '''  # + str(len(varnames))
            func, args_tb, func_pos = _analysisNotes(
                a_dict, a_dict[i].__doc__, i, a_dict[i], argcount, cmd_args, *varnames)
            if func_pos:
                module_info["_func"].insert(func_pos-1, {
                    "case": func,
                    "env": args_tb,
                })
            else:
                module_info["_func"].append({
                    "case": func,
                    "env": args_tb,
                })
        else:
            module_info["_vars"].append({i: a_dict[i]})
    return module_info


def _formatStat(ctx, funName, args_tb, stats, start_time, end_time):
    # print(TEST_START.format(ctx['__name__'],
    #                         funName, args_tb['desc'], args_tb['desc']))
    avg, max, min, sum = 0, 0, stats[0]['time'], 0
    for s in stats:
        sum = sum + s['time']
        if min > s['time']:
            min = s['time']
        if max < s['time']:
            max = s['time']
    avg = sum / len(stats)
    args_tb['stats'] = {}
    args_tb['stats']['list'] = stats
    args_tb['stats']['avg'] = avg
    args_tb['stats']['max'] = max
    args_tb['stats']['min'] = min
    print('Percentage of the call served within a certain time (ms)')
    for s in args_tb['stats']['list']:
        print("  {:>5} % \t {}".format(s['perc'], s['time']))
    print('{}.{} is Tested, Use {} (ms)\n'.format(
        ctx['__name__'], funName, end_time - start_time))
    # print(TEST_END.format(
    #     args_tb['desc'], args_tb['desc'], ctx['__name__'], funName, end_time - start_time))


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
    def call_realfunc(*dargs, **dkargs):
        start_time = int(round(time.time() * 1000))
        lis = []
        stats = []

        # 屏蔽标准输出，便于输出测试统计信息
        if None == args_tb["cmd_args"].stdout:
            stdoutbak = sys.stdout
            sys.stdout = None
        elif "" != args_tb["cmd_args"].output:  # 输出到指定文件
            pass
        else:  # 标准输出
            pass
        for _ in range(args_tb['c']):
            # p = Process(target=task1)
            def Loop(npc, n, *dargs, **dkargs):
                nonlocal stats
                if len(dargs) <= 0 or len(dargs[0]) <= 0:  # 有外部参数
                    dargs = args_tb['args']
                emptyArgs = True
                if 0 != args_tb['args_num']:
                    emptyArgs = False
                    dargs = dargs[:args_tb['args_num']]
                for _ in range(npc):
                    stat = {
                        'perc': 0,
                        'time': 0,
                    }
                    stime = int(round(time.time() * 1000))
                    try:
                        if not emptyArgs:
                            args_tb['cb'] = func(*dargs, **dkargs)
                        else:
                            args_tb['cb'] = func()
                    except Exception as e:
                        if 'FLOW' == args_tb['type']:
                            raise e
                    finally:
                        stat['perc'] = round((len(stats) + 1) * 100 / n, 1)
                        stat['time'] = int(round(time.time() * 1000)) - stime
                        stats.append(stat)
            t = Thread(target=Loop, args=[
                       args_tb['npc'], args_tb['n'], *dargs])
            lis.append(t)
            t.start()
        for t in lis:
            t.join()

        # 禁止输出
        if None == args_tb["cmd_args"].stdout:
            # 恢复标准输出
            sys.stdout = stdoutbak
        elif "" != args_tb["cmd_args"].output:  # 输出到指定文件
            pass
        else:  # 标准输出
            pass

        end_time = int(round(time.time() * 1000))
        stats = sorted(stats, key=lambda e: e['perc'], reverse=False)
        _formatStat(ctx, funName, args_tb, stats, start_time, end_time)
    return call_realfunc


def _analysisNotes(ctx, input, funName, func, argcount, cmd_args, *dargs, **dkargs):
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
    args_tb['cfg'] = input
    fun_pos = None
    try:  # json 类型
        args_tb = json.loads(input)
        args_tb['type'] = args_tb['type'].upper()
        args_tb['args_num'] = argcount
        args_tb['npc'] = math.floor(
            args_tb['n'] / args_tb['c'])  # 每个独立线程中执行的次数
        args_tb['cfg'] = input
        debug(args_tb)
    except:  # csv 类型
        input_tb = input.split(';')
        input_tb = list(map(lambda x: x.strip(), input_tb))
        args_tb['type'] = input_tb[0].upper()
        args_tb['args_num'] = argcount
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
            fun_pos = args_tb['s']
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
    args_tb['cmd_args'] = cmd_args
    # 单元测试
    if 'UNIT' == args_tb['type']:
        args_tb['desc'] = args_tb['type']
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, None
    # 并发测试
    elif 'COUNT' == args_tb['type']:
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, None
    # 流程测试
    elif 'FLOW' == args_tb['type']:
        args_tb['desc'] = args_tb['type'] + '(' + str(args_tb['s']) + "):" + \
            str(args_tb['c']) + "-" + str(args_tb['n'])
        return _genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, fun_pos
    else:
        raise TypeError("Unkonw Testing Type: " + funName)


def _parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(description='A simple test tool')
    parser.add_argument('path', nargs='?')
    parser.add_argument('-p', '--path', type=str, required=False, default="./",
                        help='test case path')
    parser.add_argument('-l', '--level', type=int, required=False, default=-1,
                        help='load module dir level')
    parser.add_argument('-t', '--type', type=str, required=False, default='a',
                        help='only test a type case: a:all u:unit c:count f:flow')
    parser.add_argument('-1', '--stdout', action="store_const",
                        const=0, help='output case stdout')
    parser.add_argument('-o', '--output', nargs='?', type=str, required=False,
                        help='output case run result into file')
    return parser.parse_args()


def loading(path, level, cur, cmd_args):
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
            module_info = _loadModule(path, filename, cmd_args)
            if module_info:
                file_tb.append(module_info)
        else:
            if not filename.startswith('.') and not filename.startswith('__'):
                loading(absPath, level, cur, cmd_args)
    return file_tb


def run(module_list):
    # debug(module_list)
    print(COPYLEFT)
    for lib in module_list:
        cb_dargs, cb_dkargs = [], {}
        for handler in lib["_func"]:
            # 流程测试
            if ("FLOW" == handler["env"]["type"]):
                handler["case"](*cb_dargs, **cb_dkargs)
                if type({}) == handler["env"]['cb']:
                    cb_dkargs = handler["env"]['cb']
                elif type(()) == handler["env"]['cb'] or type([]) == handler["env"]['cb']:
                    cb_dargs = handler["env"]['cb']
                else:
                    cb_dargs = []
                    cb_dargs.append(handler["env"]['cb'])
                # print(handler["env"])
            else:
                handler["case"]()
                # print(handler["env"])
    print(END_NOTE + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def show():
    pass


if __name__ == '__main__':
    args = _parse_args()
    # try:
    module_list = loading(args.path, args.level, 0, args)
    run(module_list)
    # except Exception as e:
    # print("Load module from {} failed ...: {}".format(args.path, e))
