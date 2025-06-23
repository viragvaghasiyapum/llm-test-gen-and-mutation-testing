import ast
import re
import mutap.utils.helper as helper

def format_testcases(code: str, id: str, run: int, function_name="has_close_elements") -> str:
    try:
        parsed = ast.parse(code)
        test_methods = []

        for i, stmt in enumerate(parsed.body[0].body):
            if isinstance(stmt, ast.Assert):
                test_name = f"test_case_{i+1}"
             
                test_code = ast.unparse(stmt).strip()
                test_code = test_code.replace("self.assert ", "assert ")
                method = [
                    f"    def {test_name}(self):",
                    f"        {test_code}"
                ]
                test_methods.append("\n".join(method))

        lines = [
            "import unittest",
            f"from output.humaneval.formatted.{id}.function import {function_name}",
            "",
            "class TestFunction(unittest.TestCase):",
            *test_methods,
            "",
            "if __name__ == '__main__':",
            "    unittest.main()"
        ]

        test_class_code = "\n".join(lines)

        path = helper.getPath('mutpy_formatted_tests', id)
        file_path = f"{path}/mutpy_testcase_run{run}.py"

        with open(file_path, "w") as f:
            f.write(test_class_code)

        return file_path

    except Exception as e:
        helper.writeTmpLog(f"Error (mupty_format_conversion): issue formatting test cases for {id} run {run} -> {e}", 'test_generation.log')
        return False


def extract_func_name(line: str) -> str:
    match = re.search(r'assert\s+([a-zA-Z_][\w]*)\s*\(', line)
    return match.group(1) if match else None