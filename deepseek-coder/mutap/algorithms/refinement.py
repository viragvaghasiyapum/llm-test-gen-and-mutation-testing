# mutap/algorithms/refinement.py
import ast
from mutap.utils.helper import writeTmpLog
from mutap.utils.helper import extract_function_name 
from typing import List, Union
import textwrap
import mutap.algorithms.test_generation as test_gen

def syntax_fix(test: str, functions: list[str]) -> str:
    try:
        fixed_test = test
        if not ast.parse(test):
            ins_fix = "# Fix the syntax errors in the following assert-based code snippet"
            prompt = f"{ins_fix}\n<code>\n{test}\n</code>\n\n<fixed>    \n"
            fixed_test = test_gen.prompt_deepseek_llmc(prompt, tag="fixed")
            fixed_test = fixed_test.strip().splitlines()
            fixed_test = '\n'.join(fixed_test);
        return syntax_check(fixed_test, functions)
    except SyntaxError as e:
        writeTmpLog(f"\nError (refinement): issue fixing syntax using LLM -> {e}.", 'test_generation.log')
        return False


def syntax_check(test: str, function_names: List[str]) -> Union[List[str], bool]:
    try:
        lines = test.splitlines()
        asserts = [line.strip() for line in lines if line.strip().startswith("assert") and any(fn in line for fn in function_names)]
        return asserts

        # # Clean indentation and strip surrounding whitespace
        # test = textwrap.dedent(test).strip()

        # # Double-check for CRLF or tab issues
        # test = test.replace('\r\n', '\n').replace('\t', '    ')

        # # Try parsing the sanitized code
        # ast.parse(test)

        # # Process lines
        # code_lines = test.splitlines()
        # final_lines = [code_lines[0]]
        # assert_flag = False

        # for line in code_lines[1:]:
        #     if line.strip().startswith("assert") and any(fn in line for fn in function_names):
        #         final_lines.append(line)
        #         assert_flag = True

        # return final_lines if assert_flag else False

    except SyntaxError as e:
        writeTmpLog(f"\nError (refinement): issue checking syntax -> {e}.", 'test_generation.log')
        return False


def intended_behavior_fix(tests: list, put_code: str) -> list:
    try:
        fixed = []
        for line in tests:
            try:
                local_env = {}
                exec(put_code, local_env)
                expr = line.strip().replace("assert", "", 1).split("==")[0].strip()
                exec(f"result = {expr}", local_env)
                actual = local_env.get("result")
                fixed.append(f"assert {expr} == {repr(actual)}")
            except Exception as e:
                print(f"Error refining a test case '{line.strip()}': {e}")
                continue
    except Exception as e:
        fixed = False
        writeTmpLog(f"\nError (refinement): issue fixing intended behaviour -> {e}.", 'test_generation.log')

    return fixed

def refine_test_cases(raw_tests: str, put_code: str, functions: list[str], task_id, run) -> list:
    try:
        lines = raw_tests.strip().splitlines()
        if not functions:
            writeTmpLog("\nError (refinement): function name(s) not defined.", 'test_generation.log')
            return '';
        syntactically_valid = syntax_fix("\n".join(lines), functions)
        if (syntactically_valid == False):
            writeTmpLog("\nError (refinement): extracting function while refining test cases.", 'test_generation.log')
            return False
        
        return intended_behavior_fix(syntactically_valid, put_code)
    except Exception as e:
        writeTmpLog(f"\nError (refinement): issue refining test cases -> {e}.", 'test_generation.log')
    return False