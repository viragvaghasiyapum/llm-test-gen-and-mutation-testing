import os
import subprocess
import mutap.utils.helper as helper
import re
from bs4 import BeautifulSoup
import yaml
import ast
from mutap.utils.helper import GCD

def run_mutation_testing(task_id: str, test_path: str, functions: list[str], run, isOracleRun=False, final_run=False):

    if (GCD.dataset == 'refactory'):
        put_path = helper.getPath('refactory_formatted_data_path') + "/" + task_id + "/reference.py"
    else:
        put_path = helper.getPath('humaneval_formatted_data_path') + "/" + task_id + "/function.py"
    out_dir = helper.getPath('mutants', task_id)
    report_dir = helper.getPath('reports', task_id)
    oracle_report_dir = helper.getPath('oracle_run', task_id)
    try:
        result = subprocess.run([
            "mut.py",
            "--target", put_path,
            "--unit-test", test_path,
            "--report-html", os.path.join(out_dir),
            "--report", os.path.join(out_dir, f"report{run}.yaml"),
            "--show-mutants"
        ], capture_output=True, text=True, check=True)
        output_lines = result.stdout.splitlines()

        if isOracleRun:
            with open(os.path.join(oracle_report_dir, f"all_mutant_single_testcase{run}.log"), "w") as log:
                for line in output_lines:
                    log.write(f"{line}\n")
        else:
            with open(os.path.join(report_dir, f"all_mutants_run{run}.log"), "w") as log:
                for line in output_lines:
                    log.write(f"{line}\n")
        
        mutant_files_path = os.path.join(out_dir, "mutants")
        extract_mutant_code(mutant_files_path, out_dir, functions)

        mutant_log_path = os.path.join(out_dir, f"report{run}.yaml")
        result = extract_mutation_summary(mutant_log_path, final_run, isOracleRun)
        
        # Clean up temporary files
        cleanup(files = [
            mutant_log_path,
            os.path.join(out_dir, "index.html"),
            mutant_files_path
        ])
        return result
    except subprocess.CalledProcessError as e:
        with open(helper.getTempFile(f"mutpy_error_run{run}_{task_id}.log"), "w") as log:
            log.write("STDOUT:\n" + e.stdout + "\n\nSTDERR:\n" + e.stderr)
        print(f"MutPy failed for {task_id}. See mutpy_error_run{run}_{task_id}.log for details.")
        
    except Exception as e:
        helper.writeTmpLog(f"\n Error (muatation_testing): issue testing mutants -> {e}", 'test_generation.log')
    return False
    

   
class IgnoreUnknownTagsLoader(yaml.SafeLoader):
    pass

def unknown_tag_handler(loader, tag_suffix, node):
    return None

IgnoreUnknownTagsLoader.add_multi_constructor('tag:', unknown_tag_handler)

def extract_mutation_summary(yaml_path, is_final_run=False, oracle_run=False):
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.load(f, Loader=IgnoreUnknownTagsLoader)

        mutation_score = data.get('mutation_score', 0.0)
        total_time = data.get('total_time', 0.0)

        survived, killed, timedout = [], [], []
        all_mutations = data.get('mutations', [])
        total_mutants = len(all_mutations)

        for m in all_mutations:
            status = m.get('status')
            file_str = f"mutant_{m.get('number')}.py"
            if status == 'survived':
                survived.append(file_str)
            if status == 'killed':
                killed.append(file_str)
            if status == 'timeout':
                timedout.append(file_str)

            # final run csv data collection
            if (is_final_run or mutation_score >= 100) and not oracle_run:
                op = m.get('mutations', [{}])[0].get('operator')
                if op is not None:
                    GCD.mutation_types[op] += 1
                    if status == 'survived':
                        GCD.survived_types[op] += 1
                    if status == 'killed':
                        GCD.killed_types[op] += 1
                    if status == 'timeout':
                        GCD.timeout_types[op] += 1

        if (is_final_run or mutation_score >= 100) and not oracle_run:
            GCD.mutation_score = mutation_score
            GCD.survived_total = len(survived)
            GCD.killed_total = len(killed)
            GCD.timeout_total = len(timedout)
            GCD.total_mutants = total_mutants
            
        return {
            "mutation_score": mutation_score,
            "survived": {'total': len(survived), 'mutants': survived},
            "killed": {'total': len(killed), 'mutants': killed},
            "total_mutants": total_mutants,
            "total_time": total_time
        }
    except Exception as e:
        helper.writeTmpLog(f"\n Error (muatation_testing): issue extracting summary -> {e}", 'test_generation.log')
        return False  

def get_function_name_at_line(code, line_no):
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'body') and node.body:
                    start = node.lineno
                    end = max(child.lineno for child in ast.walk(node) if hasattr(child, 'lineno'))
                    if start <= line_no <= end:
                        return node.name
    except Exception as e:
        helper.writeTmpLog(f"\n Error (muatation_testing): issue extracting function name at given line -> {e}", 'test_generation.log')
    return ''

def extract_mutant_code(directory, output_dir, functions):
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                mutant_file = os.path.join(root, file)
                with open(mutant_file, 'r') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                # Extract mutation ID
                heading = soup.find('h1')
                mutant_id = None
                if heading:
                    match = re.search(r'#(\d+)', heading.text)
                    if match:
                        mutant_id = int(match.group(1))

                # Extract mutated line number
                mutation_details = soup.find_all('li')
                mutation_line = None
                for item in mutation_details:
                    match = re.search(r'line (\d+)', item.text)
                    if match:
                        mutation_line = int(match.group(1))
                        break

                # Extract Python code
                pre_tag = soup.find('pre', class_=lambda c: c and 'brush: python' in c)
                if not pre_tag:
                    continue

                code = pre_tag.text.strip()

                function_str = ""
                if len(functions) > 1:
                    function_name = get_function_name_at_line(code, mutation_line) if mutation_line else None
                    function_str = f"# mutated_function_in_mutpy: ${function_name}$\n" if function_name not in ['', None] else ""

                # Save extracted code
                output_filename = f"mutant_{mutant_id or 'unknown'}.py"
                py_file_path = os.path.join(output_dir, output_filename)
                with open(py_file_path, 'w') as py_file:
                    py_file.write(function_str + code + '\n')
        return True
    except Exception as e:
        helper.writeTmpLog(f"\n Error (muatation_testing): issue extracting mutant code -> {e}", 'test_generation.log')
        return False

def cleanup(files):
    try:
        for file in files:
            if os.path.exists(file):
                if os.path.isdir(file):
                    for root, dirs, files in os.walk(file, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(file)
                else:
                    os.remove(file)
        return
    except Exception as e:
        helper.writeTmpLog(f"\n Error (muatation_testing): issue cleaning up residue files -> {e}", 'test_generation.log')
        return
