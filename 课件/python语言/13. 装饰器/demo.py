def fibonacci(n):
    if n < 3:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


print(fibonacci(40))  # 应该快速返回结果
