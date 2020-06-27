var1 = 8888
global var2


def deep_test_hello(n, m):
    '''
        # 这是一个注释
        // 这又是一种注释
        count, 10, 10, 4, 4 # 注释
    '''
    print("deep hello ptesting", n)


def deep_test_world(n):
    """
        {
            "type": 'count', # 类型
            "c": 10, # 并发数
            "n": 10, # 执行总数
            "args": ['n'] # 参数
        }
        # {"a":1,"b":2,"c":3,"d":4,"e":5}
    """
    print("deep world ptesting", n)


class A:
    def __init__(self):
        pass

    def A_func(self):
        return 'A'
