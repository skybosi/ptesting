import flower

@flower.Flower(group = "test", pri = 1, times = 3)
def test_hello():
    print("hello ptesting")