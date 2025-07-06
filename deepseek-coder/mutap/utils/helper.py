import os
from pathlib import Path
import os
import datetime
import shutil
from typing import Union
import ast 

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
        if name in {"mutants", "testcases", "prompts", "mutpy_formatted_tests"}:
            if not id:
                raise ValueError(f"ID is required for path type '{name}'")
            path = os.path.join(base_dir, "output", "humaneval", "formatted", id, name)
            check = True
        elif name == "reports":
            path = os.path.join(base_dir, "output", "humaneval", "formatted", id, "mutants", "reports")
            check = True
        elif name == "oracle_run":
            path = os.path.join(base_dir, "output", "humaneval", "formatted", id, "mutants", "reports", "oracle_run")
            check = True
        elif name == "model":
            path = os.path.join(base_dir, "model", "deepseek-coder-6.7b-base.Q4_K_M.gguf")
        elif name == "binary":
            path = os.path.join(base_dir, "buildllama", "build", "bin", "llama-cli")
        elif name == "humaneval_src":
            path = os.path.join(base_dir, "data", "humaneval", "human-eval-v2-20210705.jsonl")
        elif name == "humaneval_converted_md":
            path = os.path.join(base_dir, "data", "humaneval", "human_eval_full.md")
        elif name == "humaneval_extraction_output" or name == "formatted_humaneval":
            path = os.path.join(base_dir, "output", "humaneval", "formatted")
            check = True
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
        if cleanTemp:
            dirs = [getPath('tmp')]
        else:
            dirs = [
                getPath('prompts', id),
                getPath('mutpy_formatted_tests', id),
                getPath('mutants', id),
                getPath('testcases', id)
            ]
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