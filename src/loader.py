# -*- coding: utf-8 -*-
import importlib
import error
import sys
import re
import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


def loading(path):
    if os.sep == '\\':
        path = path.replace('/', '\\')
    elif os.sep == '/':
        path = path.replace('\\', '/')
    path_tb = path.split(os.sep)
    if '.' == path_tb[0]:
        path = cur_path + os.sep + path_tb[1]
    elif '..' == path_tb[0]:
        path = parent_path + os.sep + path_tb[1]
    elif len(path_tb) <= 1:
        path = currpath + os.sep + path_tb[0]
    else:
        path = cur_path + os.sep + path_tb[1]
    print(cur_path, currpath, path, parent_path, parentpath)
    # 获取目录下的文件与目录列表
    try:
        pathList = os.listdir(path)
    except IOError:
        return {}
    finally:
        os.sys.path.append(path)
        print(os.sys.path)
    # 遍历列表中的文件名
    for file in pathList:
        # 使用join函数对路径进行拼接，然后构成绝对路径
        if black_list.get(file) or not file.endswith('.py') or file.startswith('.'):
            continue
        if not os.path.exists(path + os.sep + '__init__.py'):
            fd = open(path + os.sep + '__init__.py', mode='w')
            fd.close()
        absPath = os.path.join(path, file)
        # 通过绝对路径判断是否是文件
        # 如果是文件，直接输出文件名
        if os.path.isfile(absPath):
            relPath = os.path.relpath(absPath)
            module_tb = relPath.split(os.sep)
            module_dir = module_tb[0]
            module_name = module_tb[1].split('.')[0]
            module_path = module_dir + '.' + module_name
            # print("module_tb:", module_tb)
            #module_name = os.path.splitext(os.path.basename(relPath))[0]
            #module_path = os.path.splitext(os.path.basename(relPath.replace(os.sep, ".")))[0]
            #m = os.path.splitext(os.path.basename(absPath))[0]
            # print(__file__, "------#:", relPath, module_path, module_name)
            # print(__file__, "------&:", module_path, "fromlist=", module_name)
            # a = __import__(module_path, fromlist = [module_name])
            a = importlib.import_module(module_name, module_path)
            # print(a)
            a_dict = a.__dict__
            module_info = {
                "_func": [],
                "_vars": [],
                "_dict": [],
                "_none": [],
                "_file": absPath,
                "_module": a
            }
            for i in a_dict:
                if -1 != str(type(a_dict[i])).find("function"):  # 函数
                    module_info["_func"].append(a_dict[i])
                elif -1 != str(type(a_dict[i])).find("dict"):  # 字典
                    module_info["_dict"].append(i)
                elif -1 != str(type(a_dict[i])).find("str"):  # 变量
                    module_info["_vars"].append(i)
                elif -1 != str(type(a_dict[i])).find("NoneType"):  # 无类型
                    module_info["_none"].append(i)
                else:
                    pass
            file_tb.append(module_info)
        else:
            # pass
            if not file.startswith('.'):
                loading(absPath)
            #raise error.Error('禁止递归加载！你是不是傻！！！')
    return file_tb


if __name__ == '__main__':
    file_tb = loading(sys.argv[1])
    print(file_tb)
