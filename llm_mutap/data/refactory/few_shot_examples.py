refactory_examples = [
    {
        "code": """def get_even_numbers(nums):\n    result = []\n    for n in nums:\n        if n % 2 == 0:\n            result.append(n)\n    return result""",
        "test": """def test():\n    assert get_even_numbers([1, 3, 5]) == []\n    assert get_even_numbers([]) == []\n"""
    },
    # {
    #     "code": """def highestk(lst, k):\n    ls = []\n    for i in range(k):\n        ls.append(max(lst))\n        lst.remove(max(lst))\n    return ls""",
    #     "test": """def test():\n    assert highestk([9, 9, 4, 9, 7, 9, 3, 1, 6], 5) == [9, 9, 9, 9, 7]\n    assert highestk([4, 5, 2, 3, 1, 6], 0) == []"""
    # },
]