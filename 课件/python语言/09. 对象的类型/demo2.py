class A:
    def foo(self):
        pass


print(type(A().foo))  # <class 'method'>
print(type(A.foo))  # <class 'function'>
print(issubclass(type(A().foo), type(A.foo)))

print(A().foo is A.foo)  # False
