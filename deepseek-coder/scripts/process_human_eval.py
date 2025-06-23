import json
import os
import re

def clean_prompt(prompt):
    # Remove docstrings (triple-quoted strings)
    prompt_no_docstring = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', '', prompt, flags=re.DOTALL)
    match = re.search(r'(def\s+\w+\s*\(.*?\):)', prompt_no_docstring, re.DOTALL)
    if match:
        return prompt_no_docstring[prompt_no_docstring.find(match.group(1)):]
    return prompt_no_docstring.strip()

def clean_test(test_code):
    # Remove METADATA dictionary
    test_code_no_meta = re.sub(r'METADATA\s*=\s*{.*?}\s*', '', test_code, flags=re.DOTALL)
    lines = test_code_no_meta.strip().split('\n')
    cleaned_lines = []
    in_docstring = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith('#') or not stripped:
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def process_jsonl(input_path, output_base_dir):
    os.makedirs(output_base_dir, exist_ok=True)
    with open(input_path, 'r') as file:
        for line in file:
            item = json.loads(line)
            taskid_number = ''.join(filter(str.isdigit, item['task_id']))
            task_dir = os.path.join(output_base_dir, 'task_' + taskid_number)
            os.makedirs(task_dir, exist_ok=True)

            cleaned_prompt = clean_prompt(item['prompt'])
            cleaned_test = clean_test(item['test'])

            function_path = os.path.join(task_dir, "function.py")
            test_path = os.path.join(task_dir, "test.py")

            with open(function_path, 'w') as f_func:
                f_func.write(cleaned_prompt + "\n" + item['canonical_solution'])

            with open(test_path, 'w') as f_test:
                f_test.write(cleaned_test)

    print("Processing complete. Output saved in:", output_base_dir)

if __name__ == "__main__":
    process_jsonl("/code/data/humaneval/human-eval-v2-20210705.jsonl", "/code/output/humaneval/formatted/")
    
