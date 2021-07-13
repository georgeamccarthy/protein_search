def partition(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
