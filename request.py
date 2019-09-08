# -*- coding: utf-8 -*-
import threading
import time
import random
import requests
import loader

def work():
    print(threading.current_thread().name)
    return
#print(locals())
#print(globals())
lib_tb = loader.loading("./")
print(lib_tb)
for lib in lib_tb:
    for i in lib["_func"]:
        try:
            i()
        except:
            continue
        finally:
            pass
#start_time = time.time()
#for i in range(1):
#    t = threading.Thread(target=work)
#    # time.sleep(1)
#    t.start()
#
#end_time = time.time()
#print('花费时间:%.2fs' % (end_time - start_time))
