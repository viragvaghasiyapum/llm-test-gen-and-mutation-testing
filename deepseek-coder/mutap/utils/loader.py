# mutap/utils/loader.py
import os

def get_problems(base_dir="output/humaneval/formatted", target=None):
    problems = []

    task_ids = ["task_" + str(target)] if target is not None else sorted(os.listdir(base_dir))

    for task_id in task_ids:
        func_path = os.path.join(base_dir, task_id, "function.py")
        if os.path.isfile(func_path):
            with open(func_path, "r") as f:
                code = f.read()
            problems.append({"task_id": task_id, "code": code})

    return problems