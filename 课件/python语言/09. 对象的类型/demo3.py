class A:
    pass


print(id(object.__repr__))
print(id(type.__repr__))
print(id(A.__repr__))  # 和object的id相同
