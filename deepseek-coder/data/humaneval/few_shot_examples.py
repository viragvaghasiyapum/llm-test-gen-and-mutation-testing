examples = [
    {
        "code": "from typing import List\ndef triangle(x: int, y: int, z: int) -> str:\n    if x == y == z:\n        return \"Equilateral triangle\"\n    elif x == y or y == z or x == z:\n        return \"Isosceles triangle\"\n    else:\n        return \"Scalene triangle\"",
        "test": "def test_triangle():\n    assert triangle(2, 2, 2) == \"Equilateral triangle\"\n    assert triangle(2, 2, 3) == \"Isosceles triangle\"\n    assert triangle(2, 3, 4) == \"Scalene triangle\""
    },
    {
        "code": "from typing import List\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False",
        "test": "def test_has_close_elements(candidate):\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False\n    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True"
    },
]