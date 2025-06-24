# mutap/utils/loader.py
import os

def get_problems(base_dir="output/humaneval/formatted"):
    problems = []
    for task_id in (os.listdir(base_dir)):
        func_path = os.path.join(base_dir, task_id, "function.py")
        if os.path.isfile(func_path):
            with open(func_path, "r") as f:
                code = f.read()
            problems.append({"task_id": task_id, "code": code})
    return problems