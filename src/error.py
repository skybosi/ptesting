# -*- coding: utf-8 -*-

ERRCODE = {
    403 : "禁止使用",
    406 : "参数不支持",
    500 : "内部异常",
}

class Error(Exception):
    def __init__(self, err):
        self.errorinfo = err
    #def __init__(self, errcode):
    #    self.errorinfo = ERRCODE[errcode]
    def __str__(self):
        return self.err
