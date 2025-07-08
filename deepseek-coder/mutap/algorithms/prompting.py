from data.humaneval.few_shot_examples import humaneval_examples
from data.refactory.few_shot_examples import refactory_examples
from mutap.utils.helper import GCD

def build_prompts(put_code, step= 'initial_prompt', function_str=None, initial_prompt='', unit_tests=''):

    llm = GCD.llm
    dataset = GCD.dataset
    type = GCD.prompt

    examples = humaneval_examples if dataset == 'humaneval' else refactory_examples

    if llm  == 'deepseek-coder':
        if step == 'syntax_fix_prompt':
                ins_fix = "# Fix the syntax errors in the following assert-based code snippet"
                return f"{ins_fix}\n<code>\n{put_code}\n</code>\n\n<fixed>    \n"
        
        elif type == "zero_shot":
            ins1 = "# Generate assert-based unit tests for the following code:"
            ins2_p1 = """\n# test case:\n<test>\ndef test():\n"""
            ins2_p2 = """    assert"""
            ins3 = "\n# FAULTY code:"
            ins4 = f"""\n# generate NEW assert-based unit tests{function_str}\n# test case:\n<test>\ndef test():\n    assert"""
            
            if step == 'initial_prompt':
                return f"{ins1}\n<code>\n{put_code}\n</code>\n{ins2_p1 + ins2_p2}"
        
            elif step == 'augmentation_prompt':
                ins3 = "# FAULTY code:"
                ins4 = f"""\n# generate NEW assert-based unit tests{function_str}\n# test case:\n<test>\ndef test():\n    assert"""
                return f"{ins3}\n<code>\n{put_code}\n</code>\n{ins4}"
        
        elif type == "few_shot":
            if step == 'initial_prompt':
                prompt = "<examples>\n"
                for example in examples:
                    prompt += f"\n<code_example>\n{example['code']}\n</code_example>\n\n<test_example>\n{example['test']}\n</test_example>\n"
                prompt += f"\n</examples>\n\n<code>\n{put_code}\n</code>\n\n<test>\ndef test():\n    assert"
                return prompt
            
            if step == 'augmentation_prompt':
                prompt = ""
                ins3 = "\n</examples>\n\n# FAULTY code:"
                ins4 = f"""\n# generate NEW assert-based unit tests{function_str}\n# test case:\n<test>\ndef test():\n    assert"""
                prompt = f"<examples>\n"
                for example in examples:
                    prompt += f"\n<code_example>\n{example['code']}\n</code_example>\n\n<test_example>\n{example['test']}\n</test_example>\n"  
                prompt += f"{ins3}\n<code>\n{put_code}\n</code>\n{ins4}"
                return prompt
        

    




# didn't worked
    # elif step == 'augmentation_prompt':
    #     unit_tests = '\t' + '\n\t'.join(unit_tests) if isinstance(unit_tests, list) else ''
    #     initial_prompt = f"<initial_prompt>\n{ins1}\n<original_code>\n{put_code}\n</original_code>\n"
    #     ins2_tweaked = f"""\n# test case:\n<initial_test>\ndef test():\n{unit_tests}\n</initial_test>\n</initial_prompt>"""
    #     initial_prompt += ins2_tweaked
    #     ins3 = "\n# The test function, test(), cannot detect the fault in the following code:"
    #     ins4 = f"""\n# generate NEW assert-based unit tests{function_str}\n# test case:\n<test>\ndef test():\n    assert"""
    #     return f"{initial_prompt}\n{ins3}\n<code>\n{put_code}\n</code>\n{ins4}"