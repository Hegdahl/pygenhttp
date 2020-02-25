def nums_to(n):
    for i in range(n):
        yield i
        print('im here')

g = nums_to(10)
