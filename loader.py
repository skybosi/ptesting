        # -*- coding: utf-8 -*-
import os
import re
import sys
import error

'''
        加载某一路径的所有python
        实现动态加载py
'''

black_list = {
    "loader.py"   : 1,
    "loader.pyc"  : 1,
    "error.py"    : 1,
    "error.pyc"   : 1,
    "request.py"  : 1,
    "request.pyc" : 1,
    "__init__.py" : 1,
    "__init__.pyc" : 1,
}

file_tb = []

def loading(path):
    # 获取目录下的文件与目录列表
    pathList = os.listdir(path)
    currpath = os.path.abspath('.')
    # 遍历列表中的文件名
    for file in pathList:
        # 使用join函数对路径进行拼接，然后构成绝对路径
        if black_list.get(file) or \
            re.match(".*\.pyc$", file) or \
            file.startswith('.'):
            print(file)
            continue
        absPath = os.path.join(path, file)
        # 通过绝对路径判断是否是文件
        # 如果是文件，直接输出文件名
        if os.path.isfile(absPath):
            if not file.endswith('py'):
                continue
            relPath = os.path.relpath(absPath)
            m = os.path.splitext(os.path.basename(relPath))[0]
            m2 = os.path.splitext(os.path.basename(relPath.replace("/", ".").replace("\\", ".")))[0]
            #m = os.path.splitext(os.path.basename(absPath))[0]
            print(relPath, m2, m)
            print(m2, "fromlist=", m)
            a = __import__(m2, fromlist=[m])
            print(a)
            a_dict = a.__dict__
            module_info = {
                "_func" : [],
                "_vars" : [],
                "_dict" : [],
                "_none" : [],
                "_file" : absPath,
                "_module": a
            }
            for i in a_dict:
                if -1 != str(type(a_dict[i])).find("function"): # 函数
                   module_info["_func"].append(a_dict[i])
                elif -1 != str(type(a_dict[i])).find("dict"): # 字典
                   module_info["_dict"].append(i)
                elif -1 != str(type(a_dict[i])).find("str"):  # 变量
                   module_info["_vars"].append(i)
                elif -1 != str(type(a_dict[i])).find("NoneType"): # 无类型
                   module_info["_none"].append(i)
                else:
                   pass
            file_tb.append(module_info)
        else:
            #pass
            if not file.startswith('.'):
                loading(absPath)
            #raise error.Error('禁止递归加载！你是不是傻！！！')
    return file_tb

if __name__ == '__main__':
    file_tb = loading(sys.argv[1])
    print(file_tb)
