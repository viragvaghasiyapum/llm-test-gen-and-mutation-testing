# mutap/algorithms/generation.py
import subprocess
import re
import mutap.utils.helper as helper
    
def prompt_deepseek_llmc(prompt, tag = "test") -> str:
    
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
            output = clean_test_output(raw_output)

    except Exception as e:
        helper.writeTmpLog(f"\n Error (test_generation): issue -> {e}", 'test_generation.log')

    return output

def extract_function_name(line: str) -> str:
    """Extract the function name from an assert line."""
    match = re.match(r"assert\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
    return match.group(1) if match else ""

def clean_test_output(raw_test_code: str) -> str:
    try:
        cleaned_asserts = []
        function_name = ""

        lines = raw_test_code.strip().splitlines()
        inside_test_func = False

        for line in lines:
            line = line.strip()

            if line.startswith("def test"):
                inside_test_func = True
                continue  # We'll add this manually later

            if not inside_test_func:
                continue

            if not line.startswith("assert "):
                continue

            if not re.match(r"assert\s+.+\s+==\s+.+", line):
                continue

            if not function_name:
                function_name = extract_function_name(line)
                if not function_name:
                    continue

            if function_name in line:
                cleaned_asserts.append("    " + line)

        # Wrap in def test(): only if we found valid asserts
        if cleaned_asserts:
            return "def test():\n" + "\n".join(cleaned_asserts)
        else:
            return ""
    except Exception as e:
        helper.writeTmpLog("\nError (test_generation): issue cleaning tests -> {e}.", 'test_generation.log')
    return ""