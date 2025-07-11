# mutap/utils/loader.py
import os
import mutap.utils.helper as helper

def get_problems(dataset: str, target: str =None) -> list[dict]:
    problems = []
    base_dir = helper.getPath(f"{dataset}_formatted_data_path")
    if dataset == 'humaneval':
        task_ids = ["task_" + target] if target is not None else sorted(os.listdir(base_dir))

        for task_id in task_ids:
            func_path = os.path.join(base_dir, task_id, "function.py")
            if os.path.isfile(func_path):
                with open(func_path, "r") as f:
                    code = f.read()
                problems.append({"task_id": task_id, "code": code})
    
    elif dataset == 'refactory':
        question_ids = ["question_" + target] if target is not None else sorted(os.listdir(base_dir))

        for task_id in question_ids:
            func_path = os.path.join(base_dir, task_id, "reference.py")
            if os.path.isfile(func_path):
                with open(func_path, "r") as f:
                    code = f.read()
                problems.append({"task_id": task_id, "code": code})

    return problems