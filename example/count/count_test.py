var1 = 8888
global var2


def deep_test_hello(n, m):
    '''
        # 这是一个注释
        // 这又是一种注释
        count;  #类型
        10, 10; # 并发控制
        4, 4 # 注释
    '''
    for _ in  range(1000000):
        pass
    return "deep_test_hello"


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
    for _ in  range(1000000):
        pass
    return "deep_test_world", n


class A:
    def __init__(self):
        pass

    def A_func(self):
        return 'A'
