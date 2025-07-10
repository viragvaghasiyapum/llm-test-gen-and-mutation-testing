# mutap/algorithms/generation.py
import subprocess
import re
import mutap.utils.helper as helper
import ast
from mutap.utils.helper import GCD
    
def prompt_deepseek_llmc(prompt, functions= [], is_fix_prompt= False, tag = "test") -> str:
    
    output = ""
    try:
        binary = helper.getPath('binary') 
        model = helper.getPath('model')

        process = subprocess.Popen([
            binary, "-m", model, "-p", prompt,
            "--n-predict", "512", "--temp", "0.2",
            "--top-p", "0.95", "--repeat-penalty", "1.1", "-ngl", "25",
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        
        full_output = process.stdout.read()
        helper.writeTmpLog("\n-----------------------\n", "deepseek_llmc.log")
        helper.writeTmpLog(full_output, "deepseek_llmc.log")
        helper.writeTmpLog("\n-----------------------\n", "deepseek_llmc.log")
        
        raw_output = ''
        if GCD.llm == 'llama2chat':
            raw_output = extract_llama_test_block(full_output, tag=tag)
        else: 
            match = re.search(rf"<{tag}>(.*?)</{tag}>", full_output, re.DOTALL)
            if match:
                raw_output = match.group(1).strip()
        
        if not raw_output:
            helper.writeTmpLog(f"\nError (test_generation): no {tag} block found in output.", 'test_generation.log')
            return ""
        output = clean_test_output(raw_output, functions=functions, is_fix_prompt=is_fix_prompt)

    except Exception as e:
        helper.writeTmpLog(f"\n Error (test_generation): issue -> {e}", 'test_generation.log')

    return output


def extract_llama_test_block(text, tag):
    # Match all [INST]...[/INST] blocks
    inst_blocks = re.findall(r'\[INST\](.*?)\[/INST\]', text, re.DOTALL)
    
    if not inst_blocks:
        return ""

    # Only use content after the last [/INST]
    post_inst_text = text.split('[/INST]', 1)[-1]

    # Search for the first <tag>...</tag> block after [/INST]
    match = re.search(rf"<{tag}>(.*?)</{tag}>", post_inst_text, re.DOTALL)
    
    return match.group(1).strip() if match else ""
    
#     return ""
# def extract_function_from_line(line):
#     try:
#         node = ast.parse(line)
#         for stmt in node.body:
#             if isinstance(stmt, ast.Assert):
#                 test = stmt.test
#                 # Pattern: assert func(...) == ...
#                 if isinstance(test, ast.Compare) and isinstance(test.left, ast.Call):
#                     func = test.left.func
#                     if isinstance(func, ast.Name):
#                         return func.id
#                 # Pattern: assert func(...)
#                 elif isinstance(test, ast.Call):
#                     func = test.func
#                     if isinstance(func, ast.Name):
#                         return func.id
#         return None
#     except SyntaxError:
#         helper.writeTmpLog("\nSyntax Error (test_generation): issue extracting function from line.", 'test_generation.log')
#     except Exception as e:
#         helper.writeTmpLog(f"\nError (test_generation): issue extracting function from line -> {e}.", 'test_generation.log')
#         return None

def clean_test_output(raw_test_code: str, functions, is_fix_prompt) -> str:
    try:
        cleaned_asserts = []
        assert_pattern = re.compile(r"^assert\s+.+\s+==\s+.+")
        lines = raw_test_code.strip().splitlines()

        for line in lines:
            line = line.strip()

            # if GCD.llm == 'deepseek-coder':
            #     if line.startswith("def test"):
            #         inside_test_func = True
            #         # print('\ndasdasdasdasd\n')
            #         continue  # We'll add this manually later

            #     if not inside_test_func:
            #         # print('\ndasasdasdasdasddasdasdasd\n')
            #         continue

            if line.endswith(","):
                line = line.rstrip(",")

            if not line.startswith("assert "):
                # print('\ndasda32341243123sdasdasd\n')
                continue

            if not assert_pattern.match(line):
                continue

            if functions and not any(fname in line for fname in functions):
                continue

            cleaned_asserts.append(line)
            if not is_fix_prompt:
                GCD.raw_tests_generated += 1
                # print('\ndasasd\n')

        if cleaned_asserts:
            return "\n".join(cleaned_asserts)
        else:
            return ""
    except Exception as e:
        helper.writeTmpLog(f"\nError (test_generation): issue cleaning tests -> {e}.", 'test_generation.log')
    return ""