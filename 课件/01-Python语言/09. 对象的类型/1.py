def a():
    pass


b = lambda: None


class A:
    @classmethod
    def foo(cls):
        pass


print(type(A))
