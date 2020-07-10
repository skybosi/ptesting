# -*- coding: utf-8 -*-
__version__ = '0.1'
__all__ = ['Requester', '__version__']

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


class Requester:
    black_list = {
        "loader.py": 1,
        "loader.pyc": 1,
        "request.py": 1,
        "request.pyc": 1,
        "__init__.py": 1,
        "__init__.pyc": 1,
    }

    DEBUG = 0

    def __init__(self, arg_str=''):
        if '' != arg_str:
            pass
        args = self._parse_args()
        self.cmd_args = args
        self.file_tb = []
        self.module_list = self.loading(args.path, args.level, 0)

    def version(self):
        return __version__

    def run(self):
        print(COPYLEFT)
        for lib in self.module_list:
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
        print(END_NOTE + time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(time.time())))

    def debug(self, *args):
        if self.DEBUG:
            print(args)

    def _initPath(self, path):
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
        self.debug(cur_path, currpath, path, parent_path, parentpath)
        return path

    def _loadModule(self, path, filename):
        '''
            加载python模块
        '''
        # 使用join函数对路径进行拼接，然后构成绝对路径
        if self.black_list.get(filename) or not filename.endswith('.py') or filename.startswith('.'):
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
        self.debug("module_tb:", module_tb)
        a = importlib.import_module(module_name, module_path)
        self.debug(a)
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
                argcount = func.__code__.co_argcount
                # 初始化分析注释，设置可能的默认值
                # 清除 // 行级注释;清除不可见字符
                cfg = re.sub('\'', '"', re.sub(
                    r'\s+', "", re.sub(r'[//|#].*', '', (a_dict[i].__doc__ or ''))))
                if type(cfg) != type("") or 0 == len(cfg):
                    cfg = '''unit;'''
                func, args_tb, func_pos = self._analysisNotes(
                    a_dict, cfg, i, a_dict[i], argcount, *varnames)
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

    def _formatStat(self, ctx, funName, args_tb, stats, start_time, end_time):
        # print(TEST_START.format(ctx['__name__'],
        #                         funName, args_tb['desc'], args_tb['desc']))
        if 'UNIT' != args_tb['type']:
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
        print('{} TEST: {}.{} is Tested, Use {} (ms)\n'.format(
            args_tb['type'], ctx['__name__'], funName, end_time - start_time))
        # print(TEST_END.format(
        #     args_tb['desc'], args_tb['desc'], ctx['__name__'], funName, end_time - start_time))

    def _genCallFunc(self, ctx, funName, func, args_tb, *dargs, **dkargs):
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
            if None == self.cmd_args.stdout:
                stdoutbak = sys.stdout
                sys.stdout = None
            elif "" != self.cmd_args.output:  # 输出到指定文件
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
                            stat['time'] = int(
                                round(time.time() * 1000)) - stime
                            stats.append(stat)
                t = Thread(target=Loop, args=[
                    args_tb['npc'], args_tb['n'], *dargs])
                lis.append(t)
                t.start()
            for t in lis:
                t.join()

            # 禁止输出
            if None == self.cmd_args.stdout:
                # 恢复标准输出
                sys.stdout = stdoutbak
            elif "" != self.cmd_args.output:  # 输出到指定文件
                pass
            else:  # 标准输出
                pass
            end_time = int(round(time.time() * 1000))
            stats = sorted(stats, key=lambda e: e['perc'], reverse=False)
            self._formatStat(ctx, funName, args_tb,
                             stats, start_time, end_time)
        return call_realfunc

    def _analysisNotes(self, ctx, input, funName, func, argcount, *dargs, **dkargs):
        '''
            分析注释中的测试控制内容
        '''
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
            self.debug(args_tb)
        except:  # 字符串类型
            # cfg = re.search(r"(unit|count|flow);([^;]*);?(.*)", input, re.I | re.M)
            cfg = re.fullmatch(
                r"(?P<type>unit|count|flow);(?P<ctrl>[^;]*)(?P<is_args>;?)(?(is_args)(?P<args>.*)|$)", input, re.I | re.M)
            if not cfg:
                raise TypeError("Unkonw Testing cfg: " + input)
            cfg_type = cfg.group('type').upper()  # or cfg.group(1).upper()
            cfg_ctrl = cfg.group('ctrl')  # or cfg.group(2)
            cfg_args = cfg.group('args')  # or cfg.group(3)
            args_tb['type'] = cfg_type

            args_tb['args_num'] = argcount
            if 'UNIT' == args_tb['type']:
                cfg_args = cfg_args.split(',')
                cfg_args = cfg_args if '' != cfg_args[0] else cfg_ctrl.split(
                    ',')
                args_tb['args'] = cfg_args
                args_tb['c'] = 1
                args_tb['n'] = 1
                args_tb['npc'] = 1
                # 必须参数检测
                if args_tb['args_num'] > len(args_tb['args']):
                    raise TypeError("Unit Testing: " + funName + ": Must " + str(args_tb['args_num']) +
                                    " Args, But Get " + str(len(args_tb['args'])))
            elif 'COUNT' == args_tb['type']:
                cfg_args = cfg_args.split(',')
                args_tb['args'] = cfg_args
                cfg_ctrl = cfg_ctrl.split(',')
                args_tb['c'] = int(cfg_ctrl[0])  # 并发数
                args_tb['n'] = int(cfg_ctrl[1])  # 并发请求的总数
                args_tb['npc'] = math.floor(
                    args_tb['n'] / args_tb['c'])  # 每个独立线程中执行的次数
                # 必须参数检测
                if args_tb['args_num'] > len(args_tb['args']):
                    raise TypeError("Count Testing: " + funName + ": Must " + str(args_tb['args_num']) +
                                    " Args, But Get " + str(len(args_tb['args'])))
            elif 'FLOW' == args_tb['type']:
                cfg_args = cfg_args.split(',')
                args_tb['args'] = cfg_args
                srt_tb = cfg_ctrl.split('-')
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
        finally:
            pass
        ctx[funName] = {}
        args_tb['desc'] = args_tb['type'] + ":" + \
            str(args_tb['c']) + "-" + str(args_tb['n'])
        # 单元测试
        if 'UNIT' == args_tb['type']:
            args_tb['desc'] = args_tb['type']
            return self._genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, None
        # 并发测试
        elif 'COUNT' == args_tb['type']:
            return self._genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, None
        # 流程测试
        elif 'FLOW' == args_tb['type']:
            args_tb['desc'] = args_tb['type'] + '(' + str(args_tb['s']) + "):" + \
                str(args_tb['c']) + "-" + str(args_tb['n'])
            return self._genCallFunc(ctx, funName, func, args_tb, *dargs, **dkargs), args_tb, fun_pos
        else:
            raise TypeError("Unkonw Testing Type: " + funName)

    def _parse_args(self):
        """Parse the args."""
        parser = argparse.ArgumentParser(description='A simple test tool')
        parser.add_argument('path', nargs='?')
        parser.add_argument('-p', '--path', type=str, required=False, default="./",
                            help='test case path')
        parser.add_argument('-L', '--level', type=int, required=False, default=-1,
                            help='load module dir level')
        parser.add_argument('-t', '--type', type=str, required=False, default='a',
                            help='only test a type case: a:all u:unit c:count f:flow')
        parser.add_argument('-1', '--stdout', action="store_const",
                            const=0, help='output case stdout')
        parser.add_argument('-o', '--output', nargs='?', type=str, required=False,
                            help='output case run result into file')
        return parser.parse_args()

    def loading(self, path, level, cur):
        '''
            加载某一路径的所有python
            实现动态加载py
            @path: 待加载的路径，支持相对路径，绝对路径
        '''
        cur = cur + 1
        if level > 0 and cur > level:
            return None
        path = self._initPath(path)
        # 获取目录下的文件与目录列表
        try:
            pathList = os.listdir(path)
        except IOError:
            raise IOError("Invalid path: ", path)
        finally:
            os.sys.path.append(path)
            self.debug(os.sys.path)
        # 遍历列表中的文件名
        for filename in pathList:
            absPath = os.path.join(path, filename)
            # 通过绝对路径判断是否是文件
            if os.path.isfile(absPath):
                module_info = self._loadModule(path, filename)
                if module_info:
                    self.file_tb.append(module_info)
            else:
                if not filename.startswith('.') and not filename.startswith('__'):
                    self.loading(absPath, level, cur)
        return self.file_tb


if __name__ == '__main__':
    r = Requester()
    r.run()
