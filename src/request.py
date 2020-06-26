# -*- coding: utf-8 -*-
import argparse
import loader
import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# argument parse


def parse_args():
    """Parse the args."""
    parser = argparse.ArgumentParser(description='A simple test tool')
    parser.add_argument('--path', type=str, required=False, default="./",
                        help='test case path')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    # print(locals()
    # print(globals())
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
