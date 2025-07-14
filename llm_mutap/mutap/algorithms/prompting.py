from data.humaneval.few_shot_examples import humaneval_examples, llama_humaneval_examples
from data.refactory.few_shot_examples import refactory_examples
from mutap.utils.helper import GCD

def build_prompts(put_code: str, step: str = 'initial_prompt', function_str: str = '', original_code: str = '', unit_tests = '', only_lhs_fixed_unit_tests = ''):

    llm = GCD.llm
    dataset = GCD.dataset
    type = GCD.prompt

    examples = humaneval_examples.copy() if dataset == 'humaneval' else refactory_examples.copy()

    if llm  == 'deepseek-coder':
        lhs_fixed_unit_tests = '\t'+ '\n\t'.join(only_lhs_fixed_unit_tests) if isinstance(only_lhs_fixed_unit_tests, list) else ''
        function_str = f" for function '{function_str}':" if function_str else ''
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
                # initial_prompt = f"# correct implementation:\n<code>\n{original_code}\n</code>\n\n # Test cases failed to detect the bug in faulty code:\n<test>\ndef test():\n{lhs_fixed_unit_tests}\n</test>\n\n"
                ins3 = "# FAULTY code:"
                ins4 = f"""\n# generate NEW assert-based unit tests{function_str}\n# test case:\n<test>\ndef test():\n    assert"""
                return f"{ins3}\n<code>\n{put_code}\n</code>\n{ins4}"
        
        elif type == "few_shot":
            if step == 'initial_prompt':
                prompt = ""
                for example in examples:
                    prompt += f"\n<code_example>\n{example['code']}\n</code_example>\n\n<test_example>\n{example['test']}\n</test_example>\n"
                prompt += f"\n# Code to test\n<code>\n{put_code}\n</code>\n\n<test>\ndef test():\n\tassert"
                return prompt
            
            if step == 'augmentation_prompt':
                prompt = ""
                ins3 = "\n# FAULTY code to test"
                ins4 = f"\n# generate NEW assert-based unit tests{function_str} that reveal the bug\n# Do NOT output anything else. Stop after </test>\n# test case:\n<test>\ndef test():\n\tassert"
                # prompt = f"<examples>\n"
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

    else:
        function_str = f" for function '{function_str}'" if function_str else ''
        unit_tests = '\n'.join(unit_tests) if isinstance(unit_tests, list) else ''
        lhs_fixed_unit_tests = '\n'.join(only_lhs_fixed_unit_tests) if isinstance(only_lhs_fixed_unit_tests, list) else ''
        if step == 'syntax_fix_prompt':
            sys_instr = "[INST]\n<<SYS>>\nYou are a Python syntax fixer. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <fixed>...</fixed>  block.\n<</SYS>>\n\n"          
            code_string = f"Please fix the syntax errors in the following assert statements:\n```python\n{put_code}\n```\n[/INST]\n"
            # output_instr = "Please fix the syntax errors in the given assert statements.\n[/INST]\n"

            return f"{sys_instr}{code_string}"

        elif type == 'zero_shot':
            if step == 'initial_prompt':

                sys_instr = "[INST]\n<<SYS>>\nYou are a Python test generator. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <test>...</test> block.\n<</SYS>>\n\n"          
                code_string = f"Please generate assert-based test cases for the following function:\n```python\n{put_code}\n```\n[/INST]\n"
                # output_instr = "Please generate assert-based test cases for the following function:\n[/INST]\n"

                return f"{sys_instr}{code_string}"
            
            elif step == 'augmentation_prompt':
                sys_instr = "[INST]\n<<SYS>>\nYou are a Python test generator. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <test>...</test>  block.\n- Output only and only new test cases.\n<</SYS>>\n\n"          
                initial_prompt = f"The following is the correct implementation:\n```python\n{original_code}\n```\n\n The following are the test cases that do NOT detect faults:\n```python\n<test>\n{unit_tests}\n</test>\n```\n\n"
                code_string = f"These fail to expose the following faulty implementation:\n```python\n{put_code}\n```\n\n"
                output_instr = f"Please generate more assert-based test cases that would pass on the correct implementation but fail on the faulty implementation{function_str}.\n[/INST]\n"
    
                # unit_tests = '\n\t'.join(unit_tests) if isinstance(unit_tests, list) else ''
                # sys_instr = "[INST]\n<<SYS>>\nYou are a Python test generator. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <test> block.\n<</SYS>>\n\n"          
                # code_string = f"```python\n{put_code}\n```\n\n"
                # output_instr = f"Please generate new assert-based test cases to detect fault {function_str} in the given faulty code.\n[/INST]\n"

                return f"{sys_instr}{initial_prompt}{code_string}{output_instr}"
            
            
        elif type == 'few_shot':
            examples = llama_humaneval_examples.copy()
            if step == 'initial_prompt':
                sys_instr = "[INST]\n<<SYS>>\nYou are a Python test generator. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <test>...</test> block.\n<</SYS>>\n\n"          
                example_str = "Here are a few examples for reference:\n"
                for example in examples:
                    example_str += f"\nExample Function:\n```python\n{example['code']}\n```\n\nExample Test Cases:\n```python\n<test>\n{example['test']}\n</test>\n```\n"
                code_string = f"\nPlease generate assert-based test cases for the following function:\n```python\n{put_code}\n```\n[/INST]\n"
                # output_instr = "Please generate assert-based test cases for the given original function.\n[/INST]\n"
                
                return f"{sys_instr}{example_str}{code_string}"
            
            elif step == 'augmentation_prompt':
                sys_instr = "[INST]\n<<SYS>>\nYou are a Python test generator. Output only Python assert statements in the format: 'assert function(input) == output'\n\n- Do NOT define any functions.\n- Do NOT add comments or explanations.\n- Do NOT include any markdown or formatting.\n- Enclose the assert statements inside a <test>...</test>  block.\n- Output only and only new test cases.\n<</SYS>>\n\n"          
                example_str = "Here are a few examples for reference:\n"
         
                for example in examples:
                    example_str += f"\nExample Function:\n```python\n{example['code']}\n```\n\nExample Test Cases:\n```python\n<test>\n{example['test']}\n</test>\n```\n"
                   
                initial_prompt = f"\nThe following is the correct implementation:\n```python\n{original_code}\n```\n\n The following are the test cases that do NOT detect faults:\n```python\n<test>\n{unit_tests}\n</test>\n```\n\n"
                code_string = f"These fail to expose the following faulty implementation:\n```python\n{put_code}\n```\n\n"
                output_instr = f"Please generate more assert-based test cases that would pass on the correct implementation but fail on the faulty implementation{function_str}.\n[/INST]\n"
                
                return f"{sys_instr}{example_str}{initial_prompt}{code_string}{output_instr}"
                
                # for llama
                # - if used examples in few-shot prompting and initial_prompt repeats asserts
                # - if not used examples in few-shot prompting equals zero-shot prompting



                # for deeepseek-coder
                # resusing insital prompt encourages model to use same input again and again for both few shot and zero shot prompting

                #remove only lhs fixed if not used