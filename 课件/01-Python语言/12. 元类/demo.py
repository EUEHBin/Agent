class MyMeta(type):
    def __call__(self, *args, **kwds):
        print("MyMeta Call")
        return super().__call__(*args, **kwds)

    def __new__(cls, name, bases, namespace):
        print("MyMeta New")
        return super().__new__(cls, name, bases, namespace)

    def __init__(self, name, bases, dict):
        print("MyMeta Init")
        super().__init__(name, bases, dict)


# 定义类
# class Dog:
#     pass


# 等效于
class Dog(metaclass=MyMeta):
    pass


# # 等效于
# Dog = type.__call__(MyMeta, "Dog", (), {})

# print(type(Dog))

# 创建实例
d = Dog()
# 等效于
# d = MyMeta.__call__(Dog)
