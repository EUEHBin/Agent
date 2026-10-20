function = type(lambda: None)

# type
print("type(type)", type(type))
print("isinstance(type, type)", isinstance(type, type))
print("isinstance(type, function)", isinstance(type, function))
print("isinstance(type, object)", isinstance(type, object))
print("\n")

# object
print("type(object)", type(object))
print("isinstance(object, type)", isinstance(object, type))
print("isinstance(object, function)", isinstance(object, function))
print("\n")

# function
print("type(function)", type(function))
print("isinstance(function, object)", isinstance(function, object))
print("isinstance(function, type)", isinstance(function, type))
print("isinstance(function, function)", isinstance(function, function))
print("\n")


# 普通对象和类
class A:
    pass


a = A()
print("type(a)", type(a))
print("type(A)", type(A))
print("isinstance(A, A)", isinstance(A, A))
print("isinstance(A, object)", isinstance(A, object))
print("isinstance(A, type)", isinstance(A, type))
print("isinstance(A, function)", isinstance(A, function))
print("isinstance(a, A)", isinstance(a, A))
print("isinstance(a, object)", isinstance(a, object))
print("isinstance(a, type)", isinstance(a, type))
print("isinstance(a, function)", isinstance(a, function))
print("\n")


# 普通函数
def func():
    pass


print("type(func)", type(func))
print("isinstance(func, object)", isinstance(func, object))
print("isinstance(func, type)", isinstance(func, type))
print("isinstance(func, function)", isinstance(func, function))
print("\n")
