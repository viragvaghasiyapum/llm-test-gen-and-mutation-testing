# mutap/algorithms/generation.py
import subprocess
import re
import mutap.utils.helper as helper
import ast
from mutap.utils.helper import GCD
    
def prompt_deepseek_llmc(prompt, is_fix_prompt= False, tag = "test") -> str:
    
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
        helper.writeTmpLog(full_output, "deepseek_llmc.log")
        test_str = f"<{tag}>(.*?)</{tag}>"
        match = re.search(test_str, full_output, re.DOTALL)
        if match:
            raw_output = match.group(1).strip()
            output = clean_test_output(raw_output, is_fix_prompt)

    except Exception as e:
        helper.writeTmpLog(f"\n Error (test_generation): issue -> {e}", 'test_generation.log')

    return output

def extract_function_from_line(line):
    try:
        node = ast.parse(line)
        for stmt in node.body:
            if isinstance(stmt, ast.Assert):
                test = stmt.test
                # Pattern: assert func(...) == ...
                if isinstance(test, ast.Compare) and isinstance(test.left, ast.Call):
                    func = test.left.func
                    if isinstance(func, ast.Name):
                        return func.id
                # Pattern: assert func(...)
                elif isinstance(test, ast.Call):
                    func = test.func
                    if isinstance(func, ast.Name):
                        return func.id
        return None
    except SyntaxError:
        helper.writeTmpLog("\nSyntax Error (test_generation): issue extracting function from line.", 'test_generation.log')
    except Exception as e:
        helper.writeTmpLog(f"\nError (test_generation): issue extracting function from line -> {e}.", 'test_generation.log')
        return None

def clean_test_output(raw_test_code: str, is_fix_prompt) -> str:
    try:
        cleaned_asserts = []
        function_name = ""

        lines = raw_test_code.strip().splitlines()
        inside_test_func = False

        for line in lines:
            line = line.strip()

            if line.startswith("def test"):
                inside_test_func = True
                # print('\ndasdasdasdasd\n')
                continue  # We'll add this manually later

            if not inside_test_func:
                # print('\ndasasdasdasdasddasdasdasd\n')
                continue

            if not line.startswith("assert "):
                # print('\ndasda32341243123sdasdasd\n')
                continue

            if not re.match(r"assert\s+.+\s+==\s+.+", line):
                # print('\ndasdasd1232313123asdasd\n')
                continue

            if not function_name:
                function_name = extract_function_from_line(line)
                
                if not function_name:
                    # print('\n123123123\n')
                    continue

            if function_name in line:
                cleaned_asserts.append(line)
                if not is_fix_prompt:
                    GCD.raw_tests_generated += 1
                # print('\ndasasd\n')

        # Wrap in def test(): only if we found valid asserts
        if cleaned_asserts:
            return "\n".join(cleaned_asserts)
        else:
            return ""
    except Exception as e:
        helper.writeTmpLog(f"\nError (test_generation): issue cleaning tests -> {e}.", 'test_generation.log')
    return ""