import os
import subprocess
import mutap.utils.helper as helper
import re
from bs4 import BeautifulSoup
import yaml

def run_mutation_testing(task_id: str, test_path: str, run, isOracleRun=False):

    put_path = helper.getPath('formatted_humaneval') + "/" + task_id + "/function.py"
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
        extract_mutant_code(mutant_files_path, out_dir)

        mutant_log_path = os.path.join(out_dir, f"report{run}.yaml")
        result = extract_mutation_summary(mutant_log_path)
        
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

def extract_mutation_summary(yaml_path):
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.load(f, Loader=IgnoreUnknownTagsLoader)

        mutation_score = data.get('mutation_score', 0.0)
        total_time = data.get('total_time', 0.0)

        survived = []
        all_mutations = data.get('mutations', [])
        total_mutants = len(all_mutations)
        killed = []

        for m in all_mutations:
            if m.get('status') == 'survived':
                survived.append(f"mutant_{m.get('number')}.py")
            if m.get('status') == 'killed':
                killed.append(m["number"])

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


def extract_mutant_code(directory, output_dir):
    try:
        for root, _, files in os.walk(directory):
            id = 0
            for file in files:
                mutant_file = os.path.join(root, file)
                
                with open(mutant_file, 'r') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                heading = soup.find('h1')
                id = None
                if heading:
                    match = re.search(r'#(\d+)', heading.text)
                    if match:
                        id = int(match.group(1))

                py_file = os.path.join(output_dir, f"mutant_{id}.py")
                pre_tag = soup.find('pre', class_=lambda c: c and 'brush: python' in c)
                
                if not pre_tag:
                    return False

                code = pre_tag.text.strip()

                with open(py_file, 'w') as py_file:
                    py_file.write(code + '\n')
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
