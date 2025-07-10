humaneval_examples = [
    # {
    #     "code": """from typing import List\ndef triangle(x: int, y: int, z: int) -> str:\n    if x == y == z:\n        return \"Equilateral triangle\"\n    elif x == y or y == z or x == z:\n        return \"Isosceles triangle\"\n    else:\n        return \"Scalene triangle\"""",
    #     "test": """def test():\n    assert triangle(2, 2, 2) == \"Equilateral triangle\"\n    assert triangle(2, 2, 3) == \"Isosceles triangle\"\n    assert triangle(2, 3, 4) == \"Scalene triangle\""""
    # },
    {
        "code": """from typing import List\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n    min_number = min(numbers)\n    max_number = max(numbers)\n    return [(x - min_number) / (max_number - min_number) for x in numbers]""",
        "test": """def test():\n    assert rescale_to_unit([2.0, 49.9]) == [0.0, 1.0]\n    assert rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]"""
    },
]

llama_humaneval_examples = [
    {
        "code": """from typing import List\ndef triangle(x: int, y: int, z: int) -> str:\n    if x == y == z:\n        return \"Equilateral triangle\"\n    elif x == y or y == z or x == z:\n        return \"Isosceles triangle\"\n    else:\n        return \"Scalene triangle\"""",
        "test": """assert triangle(2, 2, 2) == \"Equilateral triangle\"\nassert triangle(2, 2, 3) == \"Isosceles triangle\"\nassert triangle(2, 3, 4) == \"Scalene triangle\""""
    },
    # {
    #     "code": """from typing import List\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n    min_number = min(numbers)\n    max_number = max(numbers)\n    return [(x - min_number) / (max_number - min_number) for x in numbers]""",
    #     "test": """assert rescale_to_unit([2.0, 49.9]) == [0.0, 1.0]\nassert rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]"""
    # },
]