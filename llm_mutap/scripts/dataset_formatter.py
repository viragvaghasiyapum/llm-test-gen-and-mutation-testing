import os
import re
import json
import ast

def remove_docstrings(code):
    """Remove module, function, and class docstrings safely using AST."""
    class DocstringStripper(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                node.body.pop(0)
            return node

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                node.body.pop(0)
            return node

        def visit_Module(self, node):
            self.generic_visit(node)
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                node.body.pop(0)
            return node

    try:
        tree = ast.parse(code)
        stripped_tree = DocstringStripper().visit(tree)
        ast.fix_missing_locations(stripped_tree)
        return ast.unparse(stripped_tree)
    except Exception as e:
        print(f"⚠️ Failed to strip docstrings: {e}")
        return code  # fall back if something breaks

def clean_prompt(prompt):
    return remove_docstrings(prompt.strip())

def clean_test(test_code):
    # Remove METADATA dictionary
    test_code_no_meta = re.sub(r'METADATA\s*=\s*{.*?}\s*', '', test_code, flags=re.DOTALL)

    lines = test_code_no_meta.strip().splitlines()
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

def process_humaneval(input_path, output_base_dir):

    if not (os.path.exists(output_base_dir) and os.path.isdir(output_base_dir)):
        os.makedirs(output_base_dir, exist_ok=True)

        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                item = json.loads(line)
                taskid_number = ''.join(filter(str.isdigit, item['task_id']))
                task_dir = os.path.join(output_base_dir, 'task_' + taskid_number)
                os.makedirs(task_dir, exist_ok=True)

                # Clean prompt and test
                cleaned_prompt = clean_prompt(item['prompt'])
                cleaned_test = clean_test(item['test'])

                # Write function.py
                function_path = os.path.join(task_dir, "function.py")
                with open(function_path, 'w', encoding='utf-8') as f_func:
                    f_func.write(cleaned_prompt + "\n" + item['canonical_solution'])

                # Write test.py
                test_path = os.path.join(task_dir, "test.py")
                with open(test_path, 'w', encoding='utf-8') as f_test:
                    f_test.write(cleaned_test)

        print("✅ Processing complete. Output saved in:", output_base_dir)
    else:
        print("✅ HumanEval already formatted.\n")

def clean_python_code(code):
    class DocstringRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Str)):
                node.body.pop(0)  # remove function docstring
            return node

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Str)):
                node.body.pop(0)  # remove class docstring
            return node

        def visit_Module(self, node):
            self.generic_visit(node)
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Str)):
                node.body.pop(0)  # remove module-level docstring
            return node

    try:
        tree = ast.parse(code)
        cleaned_tree = DocstringRemover().visit(tree)
        ast.fix_missing_locations(cleaned_tree)
        return ast.unparse(cleaned_tree)
    except Exception as e:
        print(f"⚠️ Failed to clean docstrings: {e}")
        return code  # fallback to original code

def copy_and_clean(src_path, dst_folder):
    with open(src_path, 'r', encoding='utf-8') as f:
        raw_code = f.read()
    cleaned_code = clean_python_code(raw_code)
    dst_file = os.path.join(dst_folder, os.path.basename(src_path))
    with open(dst_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_code)


def process_refactory(input_path, output_base_dir):
    if not (os.path.exists(output_base_dir) and os.path.isdir(output_base_dir)):
        # Loop through all question directories
        for question_dir in os.listdir(input_path):
            q_path = os.path.join(input_path, question_dir)
            code_dir = os.path.join(q_path, 'code')
            if not os.path.isdir(code_dir):
                continue

            print(f"Processing: {question_dir}")
            reference_file = os.path.join(code_dir, 'reference', 'reference.py')
            wrong_dir = os.path.join(code_dir, 'wrong')

            # Destination folder: cleaned_output/question_1/
            dst_question_dir = os.path.join(output_base_dir, question_dir)
            os.makedirs(dst_question_dir, exist_ok=True)

            # Copy and clean reference.py
            if os.path.isfile(reference_file):
                copy_and_clean(reference_file, dst_question_dir)

            wrong_dst_dir = os.path.join(dst_question_dir, 'wrong')
            os.makedirs(wrong_dst_dir, exist_ok=True)
            # Copy and clean first 20 wrong/*.py files
            wrong_files = sorted(f for f in os.listdir(wrong_dir) if f.endswith('.py'))
            for f in wrong_files[:20]:
                copy_and_clean(os.path.join(wrong_dir, f), wrong_dst_dir)

        print("✅ All questions processed and cleaned.")
    
    else:
        print("✅ Refactory already formatted.\n")