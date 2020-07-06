def flow_test_1(n, m):
    '''
        flow; eg1:1-3, 2, 3; 1, 1, 'test'
    '''
    for _ in range(100000):
        pass
    return "flow:" + '1-3'


def flow_test_2(n):
    """
        flow; eg1:2-3-4-2,2; 1, 1, 'test'
    """
    for _ in range(200000):
        pass
    rest = n + " -> flow:2-3"
    print(rest)
    return rest


def flow_test_3(n):
    """
        flow; eg1:3-3,2; 1, 1, 'test'
    """
    for _ in range(300000):
        pass
    rest = n + " -> flow:3-3; "
    print(rest)
    return rest
