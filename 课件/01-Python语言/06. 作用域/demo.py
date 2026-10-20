def add_item(item, items=[]):
    items.append(item)
    return items


print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] —— 意外！列表被共享了
