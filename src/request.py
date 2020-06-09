# -*- coding: utf-8 -*-  
import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import threading
import time
import random
# import requests
import loader
import argparse

# print(os.sys.path)

def work():
    print(threading.current_thread().name)
    return

# argument parse
def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(description='A simple test tool')
    parser.add_argument('--path', type=str, required=False, default="./",
                        help='test case path')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    #print(locals()
    #print(globals())
    lib_tb = loader.loading(args.path)
    # print(lib_tb)
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