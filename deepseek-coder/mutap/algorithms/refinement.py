# mutap/algorithms/refinement.py
import ast
from mutap.utils.helper import writeTmpLog
from typing import List, Union
import mutap.algorithms.test_generation as test_gen
from mutap.algorithms.prompting import build_prompts
from mutap.utils.helper import GCD

def syntax_fix(test: str, functions: list[str]) -> str:
    try:
        llm_fixed = 0
        fixed_test = test
        fix = False
        try:
            tree = ast.parse(test)
            if not tree:
                fix = True
        except SyntaxError as e:
            fix = True
        
        if fix:
            prompt = build_prompts(test, step='syntax_fix_prompt')
            fixed_test = test_gen.prompt_deepseek_llmc(prompt, functions=functions, is_fix_prompt=True, tag='fixed')
            fixed_test = fixed_test.strip().splitlines()
            fixed_test = '\n'.join(fixed_test);
            llm_fixed = 1
            GCD.fixed_by_model += 1
            
        GCD.syntax_errored += llm_fixed
        return syntax_check(fixed_test, functions, llm_fixed)
    
    # except SyntaxError as e:
    #     writeTmpLog(f"\nSynatx Error (refinement): issue fixing syntax using LLM -> {e}.", 'test_generation.log')
    except Exception as e:
        writeTmpLog(f"\Error (refinement): issue fixing syntax using LLM -> {e}.", 'test_generation.log')
        exit(50)
    return False


def syntax_check(test: str, function_names: List[str], llm_fixed, error_line= None) -> Union[List[str], bool]:
    lines = []
    result = False
    code = test.strip()
    # ommited = 0
    try:
        lines = code.splitlines()
        if error_line is not None and 0 < error_line <= len(lines):
            del lines[error_line - 1]
            # ommited = 1
            GCD.fixed_by_ommiting += 1
            code = "\n".join(lines)
        tree = ast.parse(code)
        if tree:
            cleaned_code = ast.unparse(tree).splitlines()
            asserts = [line.strip() for line in cleaned_code if line.strip().startswith("assert") and any(fn in line for fn in function_names)]
            result = asserts if asserts else False
        
    except SyntaxError as e:
        result = syntax_check(code, function_names, e.lineno)
        # ommited = 1
    except Exception as e:
        writeTmpLog(f"\nError (refinement): issue checking syntax -> {e}.", 'test_generation.log')
        exit(51)
        result = False
    # if ommited == 0 and llm_fixed == 1:
    #     GCD.fixed_by_model += 1
    return result

def intended_behavior_fix(tests: list, put_code: str) -> list:
    try:
        fixed = []
        only_lhs_fixed = []
        errored = False
        for line in tests:
            try:
                local_env = {}
                exec(put_code, local_env)
                expr = line.strip().replace("assert", "", 1).strip()
                expr = expr.split("==", 1)
                expr_lhs = expr[0].strip()
                expr_rhs = expr[1].strip() if len(expr) > 1 else None
                exec(f"result = {expr_lhs}", local_env)
                actual = local_env.get("result")
                fixed.append(f"assert {expr_lhs} == {repr(actual)}")
                generated = eval(expr_rhs, local_env)
                only_lhs_fixed.append(f"assert {expr_lhs} == {repr(generated)}")
                if not generated == actual:
                    errored = True
                    GCD.ibf_repaired += 1
            except Exception as e:
                errored = True
                GCD.ibf_unrepaired += 1
                print(f"Error behaviour fixing a test case, skipping... '{line.strip()}': {e}")
                continue
        if errored:
            GCD.ibf_assertion_errored += 1
    except Exception as e:
        fixed = only_lhs_fixed = False
        writeTmpLog(f"\nError (refinement): issue fixing intended behaviour -> {e}.", 'test_generation.log')

    return fixed, only_lhs_fixed

def refine_test_cases(raw_tests: str, put_code: str, functions: list[str], task_id, run) -> list:
    try:
        lines = raw_tests.strip().splitlines()
        if not functions:
            writeTmpLog("\nError (refinement): function name(s) not defined.", 'test_generation.log')
            exit(52)
            return False, False;
        syntactically_valid = syntax_fix("\n".join(lines), functions)
        if (syntactically_valid == False):
            writeTmpLog("\nError (refinement): issue extracting function while refining test cases.", 'test_generation.log')
            return False, False
        return intended_behavior_fix(syntactically_valid, put_code)
    except Exception as e:
        writeTmpLog(f"\nError (refinement): issue refining test cases -> {e}.", 'test_generation.log')
        exit(53)
    return False, False