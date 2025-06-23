import os
from pathlib import Path
import os

def save_checkpoint(task_id: str, run: int, label: str, content: str):
    try:
        out_dir = getPath(label, task_id)
        filename = f"{label}_run{run}_{task_id}.py"
        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return str(filepath)
    except Exception as e:
        print(f"Error saving checkpoint for {task_id} run {run} label {label}: {e}")
        return False

def getPath(name, id=None):
    try:
        base_dir = getRootDir()
        if base_dir is None:
            raise ValueError("Base directory could not be resolved.")

        check = False
        path = None
        if name in {"mutants", "testcases", "prompts", "refinement"}:
            if not id:
                raise ValueError(f"ID is required for path type '{name}'")
            path = os.path.join(base_dir, "output", "humaneval", "formatted", id, name)
            check = True
        elif name == "reports":
            path = os.path.join(base_dir, "output", "humaneval", "formatted", id, "mutants", "reports")
            check = True
        elif name == "model":
            path = os.path.join(base_dir, "model", "deepseek-coder-6.7b-base.Q4_K_M.gguf")
        elif name == "binary":
            path = os.path.join(base_dir, "llama.cpp", "build", "bin", "llama-cli")
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
    
def py_file_reader(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return ""
    
def writeLog(content: str, name: str) -> bool:
    try:
        tmp_dir = getPath('tmp')
        file_path = os.path.join(tmp_dir, name)
        with open(file_path, 'a') as file:
            file.write(content + "\n")
        return True
    except Exception as e:
        print(f"Error writing to log file '{file_path}': {e}")
        return False