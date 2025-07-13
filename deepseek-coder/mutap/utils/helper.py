import os
from pathlib import Path
import os
import datetime
import shutil
from typing import Union
import ast 
import csv
from collections import defaultdict
import json

def save_checkpoint(name: str, label: str, content: str, task_id: str) -> Union[str, bool]:
    try:
        out_dir = getPath(label, task_id)
        filepath = os.path.join(out_dir, name)
        with open(filepath, "w") as f:
            f.write(content)
        return str(filepath)
    except Exception as e:
        print(f"\nError saving checkpoint for {name}: {e}\n\n")
        return False

def getPath(name, id=None):
    try:
        base_dir = getRootDir()
        if base_dir is None:
            raise ValueError("Base directory could not be resolved.")

        check = False
        path = None
        dataset = GCD.dataset
        if name in {"mutants", "testcases", "prompts", "mutpy_formatted_tests"}:
            if not id:
                raise ValueError(f"ID is required for path type '{name}'")
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, name)
            check = True
        elif name == "reports":
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, "mutants", "reports")
            check = True
        elif name == "mutpy_oracle_formatted_tests":
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, "mutpy_formatted_tests", "oracle_run")
            check = True
        elif name == "refactory_buggy_dir":
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, "wrong")
        elif name == "buggy_unittests_run":
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, name)
            check = True
        elif name == "buggy_unittests_run_report":
            path = os.path.join(base_dir, "output", f"{dataset}", "analysis_reports", "buggy_code_run", "reports", f"{GCD.task_id}")
            check = True
        elif name == "oracle_run":
            path = os.path.join(base_dir, "output", f"{dataset}", "formatted", id, "mutants", "reports", "oracle_run")
            check = True
        elif name == "model":
            if GCD.llm == "llama2chat":
                return os.path.join(base_dir, "model", "llama-2-7b-chat.Q4_K_M.gguf")
            else: 
                return os.path.join(base_dir, "model", "deepseek-coder-6.7b-base.Q4_K_M.gguf")
        elif name == "binary":
            path = os.path.join(base_dir, "buildllama", "build", "bin", "llama-cli")
        elif name == "analysis_report_path":
            path = os.path.join(base_dir, "output", f"{dataset}", "analysis_reports")
            check = True
        elif name == "buggy_code_run_analysis_path":
            path = os.path.join(base_dir, "output", f"{dataset}", "analysis_reports", "buggy_code_run")
            check = True
        elif name == "humaneval_src":
            path = os.path.join(base_dir, "data", "humaneval", "human-eval-v2-20210705.jsonl")
        elif name == "refactory_src":
            path = os.path.join(base_dir, "data", "refactory")
        elif name == "humaneval_converted_md":
            path = os.path.join(base_dir, "data", "humaneval", "human_eval_full.md")
        elif name == "humaneval_formatted_data_path":
            path = os.path.join(base_dir, "output", "humaneval", "formatted")
        elif name == "refactory_formatted_data_path":
            path = os.path.join(base_dir, "output", "refactory", "formatted")
        elif name == "tmp":
            path = os.path.join(base_dir, "tmp")
            check = True
        else:
            raise KeyError(f"Unrecognized path name: '{name}'")

        if check:
            isExistOrCreate(path)    
        return path

    except Exception as e:
        print(f"Error getting path for '{name}' (id={id}): {e}")
        return None
    
def getRootDir() -> str:
    return str(Path(__file__).resolve().parents[2])

def getTempFile(file: str):
    try:
        temp_dir = os.path.join(getRootDir(), "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        return os.path.join(temp_dir, file)
    except Exception as e:
        print(f"Error creating temp file for '{file}': {e}")
        return None
    
def isExistOrCreate(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Error crreating path '{path}': {e}")
        return False

def writeTmpLog(content: str, name: str) -> bool:
    try:
        tmp_dir = getPath('tmp')
        file_path = os.path.join(tmp_dir, name)
        with open(file_path, 'a') as file:
            file.write(content + "\n")
        return True
    except Exception as e:
        print(f"Error writing to log file '{file_path}': {e}")
        return False

def cleanOldRunFiles(id= None, cleanTemp= False):
    try:
        dataset = GCD.dataset
        if cleanTemp:
            dirs = [getPath('tmp')]
        else:
            dirs = [
                getPath('prompts', id),
                getPath('mutpy_formatted_tests', id),
                getPath('mutants', id),
                getPath('testcases', id)
            ]
            if dataset == 'refactory':
                dirs.append(getPath('buggy_unittests_run', id))
        for path in dirs:
            shutil.rmtree(path)
            print(f"Cleaned old runs files from path: {path}..")
    except Exception as e:
        print(f"Error cleaning old runs: {e}")


def writeReportLog(file, dir, info, content: str, taskId, run) -> bool:
    
    heading = f"/*\n=============================================\n\tTask: {taskId}\n\tInfo: {info}\n\tTime: {datetime.datetime.now()}\n=============================================\n*/\n"

    start_str = f"\n------------------------------\n| Run: {run} (start) |\n------------------------------\n"
    end_str = f"\n------------------------------\n| Run: {run} (end) |\n------------------------------\n"

    try:
        report_dir = getPath(dir, taskId)
        if not report_dir:
            print(f"Report directory for {file} could not be resolved.")
            return False
        
        file_path = os.path.join(report_dir, file)
        if not os.path.exists(file_path):
            content = heading + start_str + content + end_str
        else:
            content = start_str + content + end_str
        with open(file_path, 'a') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing report log for {file}: {e}")
        return False
    
def write_buggy_report(content, filename):
    try:
        dir = getPath('buggy_unittests_run_report')
        with open(os.path.join(dir, filename), 'a') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing buggy report for {filename}: {e}")
        return False
    
def extract_function_name(code: str) -> list[str]:
    try:
        parsed = ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return []

    function_names = []
    for node in parsed.body:
        if isinstance(node, ast.FunctionDef):
            function_names.append(node.name)

    return function_names

# Global Class to hold data for the pipeline for each task (Global Class Data)
class GCD:
    # run info
    task_id = dataset = method = prompt = llm = ''
    run = subrun = 0

    # mutation info
    mutation_score = 0.0
    problematic_put = total_mutants = survived_total = killed_total = timeout_total = 0
    mutation_types, survived_types, killed_types, timeout_types = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    
    # testcases info
    final_tests = ''
    raw_tests_generated = refined_tests = duplicate_tests_removed = 0
    syntax_errored = fixed_by_model = fixed_by_ommiting = 0
    ibf_assertion_errored = ibf_repaired = ibf_unrepaired = 0
    
    @classmethod
    def reset(cls, full_reset= False, mutation_reset= False, normal_reset= False):
        
        if full_reset:
            # run info
            cls.task_id = cls.dataset = cls.method = cls.prompt = cls.llm =  ''
            normal_reset = True

        if normal_reset:
            cls.run = cls.subrun = cls.problematic_put = 0
            # testcases info
            cls.final_tests = ''
            cls.raw_tests_generated = cls.refined_tests = cls.duplicate_tests_removed = 0
            cls.syntax_errored = cls.fixed_by_model = cls.fixed_by_ommiting = cls.ibf_assertion_errored = cls.ibf_repaired = cls.ibf_unrepaired = 0
            mutation_reset = True
        
        if mutation_reset:
            # mutation info
            cls.mutation_score = 0.0
            cls.total_mutants = cls.survived_total = cls.killed_total = cls.timeout_total = 0
            cls.mutation_types, cls.survived_types, cls.killed_types, cls.timeout_types = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
        
        

def write_mutap_analysis():
    
    try:
        header = ['task_id', 'dataset', 'method', 'prompt', 'llm', 'run', 'subrun', 'problematic_put', 'final_tests', 'mutation_score', 'mutation_types', 'total_mutants', 'survived_total', 'survived_types', 'killed_total', 'killed_types', 'timeout_total', 'timeout_types', 'raw_tests_generated', 'refined_tests' ,'duplicate_tests_removed', 'syntax_errored', 'fixed_by_model', 'fixed_by_ommiting', 'ibf_assertion_errored', 'ibf_repaired', 'ibf_unrepaired']

        # Row data
        row = {
            'task_id'        : GCD.task_id,
            'dataset'        : GCD.dataset,
            'method'         : GCD.method,
            'prompt'         : GCD.prompt,
            'llm'            : GCD.llm,
            'run'            : GCD.run,
            'subrun'         : GCD.subrun,
            'problematic_put': GCD.problematic_put,
            'final_tests'    : GCD.final_tests,

            'mutation_score': GCD.mutation_score,
            'total_mutants' : GCD.total_mutants,
            'survived_total': GCD.survived_total,
            'killed_total'  : GCD.killed_total,
            'timeout_total' : GCD.timeout_total,

            'mutation_types': json.dumps(GCD.mutation_types),
            'survived_types': json.dumps(GCD.survived_types),
            'killed_types'  : json.dumps(GCD.killed_types),
            'timeout_types' : json.dumps(GCD.timeout_types),

            'raw_tests_generated'    : GCD.raw_tests_generated,
            'refined_tests'          : GCD.refined_tests,
            'duplicate_tests_removed': GCD.duplicate_tests_removed,
            'syntax_errored'         : GCD.syntax_errored,
            'fixed_by_model'         : GCD.fixed_by_model,
            'fixed_by_ommiting'      : GCD.fixed_by_ommiting,
            'ibf_assertion_errored'  : GCD.ibf_assertion_errored,
            'ibf_repaired'           : GCD.ibf_repaired,
            'ibf_unrepaired'         : GCD.ibf_unrepaired,
        }

        output_path = os.path.join(getPath('analysis_report_path'), f"{GCD.prompt}_{GCD.dataset}_{GCD.llm}.csv")
        write_header = not os.path.exists(output_path) or os.path.getsize(output_path) == 0
        with open(output_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if write_header:
                write_header = False
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"Error writing Mutap analysis report: {e}")
        exit(80)

def write_buggy_code_run_analysis(data: list[dict]):
    try:
        header = ['question_id', 'task_id', 'dataset', 'method', 'llm', 'total_buggy_codes', 'killed', 'survived', 'total_testcases', 'timeout']
        output_path = os.path.join(getPath('buggy_code_run_analysis_path'), f"{GCD.prompt}_{GCD.dataset}_{GCD.llm}_buggy_code_run.csv")
        write_header = not os.path.exists(output_path) or os.path.getsize(output_path) == 0
        with open(output_path, 'a', newline='') as f:
            for row in data:
                writer = csv.DictWriter(f, fieldnames=header)
                if write_header:
                    write_header = False
                    writer.writeheader()
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing buggy code run analysis: {e}")
        exit(81)