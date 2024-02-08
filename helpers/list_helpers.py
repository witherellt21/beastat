def intersection(lst1: list, lst2:list) -> list:
    """Get the intersection of two lists"""
    lst3 = [value for value in lst1 if value in lst2]
    return lst3