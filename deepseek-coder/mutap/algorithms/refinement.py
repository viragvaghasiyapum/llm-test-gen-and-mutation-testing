# mutap/algorithms/refinement.py
import ast
import re
from mutap.utils.helper import writeTmpLog 

# Do not work
# def syntax_fix(test: str, put_code) -> str:
#     allowed_run = 10
#     try:
        
#         if False and syntax_check(test, function_name):
#             return test
#         else:
#             # ins1 = "# each assert statement should include correct function name: {function_name} and keyword: assert"
#             ins2 = "# fix assert-based unit tests syntax like `assert has_close_elements(`:"
            

#             print(function_name)
#             print("\n\n")
#             print(test)
#             print("\n\n")

#             test = "def test():\r\n    asst has_elements([1, 3], 0.5) == True\r\n    ert close_elements([1, 2], 0.5) == False\r\n     ([1, 4], 0.5) == False"
#             prompt = f"{ins2}\n<test>\n{test}\n</test>\n"

#             print("\n\n")
#             print(prompt)
#             print("\n\n")
#             while allowed_run > 0:
#                 syntax_fixed_test = test_gen.prompt_deepseek_llmc(prompt)
#                 print("\n\n")
#                 if (syntax_check(syntax_fixed_test, function_name)):
#                     print(syntax_fixed_test)
#                     return syntax_fixed_test
#                 allowed_run -= 1
#     except SyntaxError as e:
#         return "\n".join(test.splitlines()[:e.lineno - 1])


def syntax_check(test, function_name: str) -> bool:
    try:
        if ast.parse(test):
            code = test.strip().splitlines()
            final_lines = [code[0]]
            code = code[1:]
            assert_flag = False
            for line in code:
                if line.strip().startswith("assert") and function_name in line:
                    final_lines.append(line)
                    assert_flag = True
            return final_lines if assert_flag else False
    except SyntaxError:
        return False


def intended_behavior_fix(tests: list, put_code: str) -> list:
    try:
        fixed = [tests[0]]
        for line in tests[1:]:
            try:
                local_env = {}
                expr = line.strip().replace("assert", "", 1).split("==")[0].strip()
                exec(put_code + f"\nresult = {expr}", {}, local_env)
                actual = local_env.get("result")
                fixed.append(f"\tassert {expr} == {repr(actual)}")
            except Exception as e:
                print(f"Error refining a test case '{line.strip()}': {e}")
                continue
    except Exception as e:
        fixed = False
        writeTmpLog("\nError (refinement): issue fixing intended behaviour -> {e}.", 'test_generation.log')
    return fixed

def refine_test_cases(raw_tests: str, put_code: str, task_id, run) -> list:
    try: 
        lines = raw_tests.strip().splitlines()
        function_name = extract_function_name(put_code)
        if not function_name:
            writeTmpLog("\nError (refinement): extracting function while refining test cases.", 'test_generation.log')
            return '';
        # syntactically_valid = syntax_fix("\n".join(lines), put_code)
        syntactically_valid = syntax_check("\n".join(lines), function_name)
        if (syntactically_valid == False):
            writeTmpLog("\nError (refinement): extracting function while refining test cases.", 'test_generation.log')
            return False
        return intended_behavior_fix(syntactically_valid, put_code)
    except Exception as e:
        writeTmpLog("\nError (refinement): issue refining test cases -> {e}.", 'test_generation.log')
    return False

def extract_function_name(code_str: str) -> str:
    match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code_str)
    return match.group(1) if match else False 