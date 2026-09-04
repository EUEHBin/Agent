def to_linked_list(iterable):
    result = {}
    len = len(iterable)
    for i,value in iterable:
        if i < len:
            result["value"] = value
            result["next"] = to_linked_list(iterable[i+1:])




linked1 = to_linked_list((1, 2, 3))
print(linked1)
# {'value': 1, 'next': {'value': 2, 'next': {'value': 3, 'next': None}}}

linked2 = to_linked_list([10, 20])
print(linked2)
# {'value': 10, 'next': {'value': 20, 'next': None}}

print(to_linked_list([]))  # None