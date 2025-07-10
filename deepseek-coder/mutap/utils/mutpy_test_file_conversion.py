import ast
import re
import mutap.utils.helper as helper
from mutap.utils.helper import GCD

def format_testcases(code: str, id: str, run: int, function_name: list[str] = [], is_oracle_run= False, buggy_file= False) -> str:
    try:
        parsed = ast.parse(code)
        test_methods = []

        for i, stmt in enumerate(parsed.body):
            if isinstance(stmt, ast.Assert):
                test_name = f"test_case_{i+1}"
             
                test_code = ast.unparse(stmt).strip()
                test_code = test_code.replace("self.assert ", "assert ")
                method = [
                    f"    def {test_name}(self):",
                    f"        {test_code}"
                ]
                test_methods.append("\n".join(method))

        file_name = 'function'
        if GCD.dataset == 'refactory' and buggy_file is not False:
            file_name = f"wrong.{buggy_file}"
        elif GCD.dataset == 'refactory':
            file_name = 'reference'
        lines = [
            "import unittest",
            f"from output.{GCD.dataset}.formatted.{id}.{file_name} import {', '.join(function_name)}",
            "",
            "class TestFunction(unittest.TestCase):",
            *test_methods,
            "",
            "if __name__ == '__main__':",
            "    unittest.main()"
        ]
        test_class_code = "\n".join(lines)

        path_str = 'mutpy_formatted_tests'
        if GCD.dataset == 'refactory' and buggy_file is not False:
            path_str = 'buggy_unittests_run'
        elif is_oracle_run:
            path_str = 'mutpy_oracle_formatted_tests'

        path = helper.getPath(path_str, id)

        file_path = f"{path}/mutpy_testcase_run{run}.py"
        if GCD.dataset == 'refactory' and buggy_file is not False:
            file_path = f"{path}/mutpy_{buggy_file}.py"
        elif is_oracle_run:
            file_path = f"{path}/mutpy_testcase_{run}.py"

        with open(file_path, "w") as f:
            f.write(test_class_code)

        return file_path

    except Exception as e:
        helper.writeTmpLog(f"Error (mupty_format_conversion): issue formatting test cases for {id} run {run} -> {e}", 'test_generation.log')
        return False


def extract_func_name(line: str) -> str:
    match = re.search(r'assert\s+([a-zA-Z_][\w]*)\s*\(', line)
    return match.group(1) if match else None