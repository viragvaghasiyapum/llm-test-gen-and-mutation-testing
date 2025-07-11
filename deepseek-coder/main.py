from mutap.pipeline import run_pipeline
from scripts.dataset_formatter import process_humaneval, process_refactory
import mutap.utils.helper as helper
# from test_pynguin.pynguin_test import execute_pynguin_test
import os

def main():
    while True:
        print("\n--------------- Effective Test Generation Using Pre-Trained LLM & Mutation Testing ---------------\n")
        print("Choose Pipeline Parameters:")

        # Dataset selection
        print("\nSelect Dataset:")
        print("1. HumanEval")
        print("2. Refactory")
        dataset_choice = input("✅ Enter dataset [1/2]: ").strip()
        dataset = "humaneval" if dataset_choice == '1' else "refactory" if dataset_choice == '2' else None
        if dataset is None:
            print("❌ Invalid dataset. Try again.")
            continue

        # Limit input
        limit = get_task_limit(dataset)

        # initial prompt type selection
        print("\nSelect Prompt Type:")
        print("1. Run with Zero-Shot Prompt")
        print("2. Run with Few-Shot Prompt")
        prompt_choice = input("✅ Enter prompt type [1/2]: ").strip()

        if prompt_choice not in {'1', '2'}:
            print("❌ Invalid prompt type. Try again.")
            continue
        prompt_mode = "zero_shot" if prompt_choice == '1' else "few_shot"

        # LLM selection
        print("\nSelect LLM:")
        print("1. LLaMA-2-Chat-7b-Q4-KM.gguf")
        print("2. Deepseek-Coder-7b-Q4-KM.gguf")
        llm_choice = input("✅ Enter LLM [1/2]: ").strip()

        llm = "llama2chat" if llm_choice == '1' else "deepseek-coder" if llm_choice == '2' else None
        if llm is None:
            print("❌ Invalid LLM choice. Try again.")
            continue

        # Method selection
        print("\nSelect Test Generation Method:")
        print("1. Before Refining")
        print("2. After Refining")
        print("3. Full MuTAP (mutation + prompt augmentation)")
        print("4. Pynguin")
        method_choice = input("✅ Enter method [1-4]: ").strip()

        method_map = {
            '1': 'before_refining',
            '2': 'after_refining',
            '3': 'mutap',
            '4': 'pynguin'
        }
        method = method_map.get(method_choice)
        if method is None:
            print("❌ Invalid method. Try again.")
            continue

        # Display selected parameters
        print(f"\n🚀 Running pipeline:")
        print(f"→ Prompt Mode: {prompt_mode}")
        print(f"→ LLM: {llm}")
        print(f"→ Method: {method}")
        print(f"→ Limit: {limit}")

        # Run pipeline
        if method == "pynguin":
            # run_pynguin_pipeline(limit=limit)
            # execute_pynguin_test(limit, dataset)
            print('Work in progress for Pynguin test generation...')
        else:
            run_pipeline(limit, prompt_mode, llm, method, dataset)

        again = input("\n\nRun another test? (y/n): ").strip().lower()
        if again != 'y':
            break

def get_task_limit(dataset):
    print("\nSelect how to run:")
    print("1. Run all tasks")
    print("2. Run a specific task")
    print("3. Run a fixed number of tasks")

    while True:
        mode = input("✅ Enter mode (1/2/3): ").strip()

        if mode == "1":
            return {'type': 'all', 'value': None}

        elif mode == "2":
            max_task = 164 if dataset == "humaneval" else 5
            start_point = 0 if dataset == "humaneval" else 1
            task_input = input(f"🔢 Enter task number ({start_point} to {max_task}): ").strip()
            try:
                task_number = int(task_input)
                if start_point <= task_number <= max_task:
                    return {'type': 'specific', 'value': task_number}
                else:
                    print(f"❌ Task number out of range ({start_point} to {max_task}).")
            except ValueError:
                print("❌ Invalid task format. Use format like 25.")

        elif mode == "3":
            count_input = input("🔢 Enter number of tasks to run: ").strip()
            if count_input.isdigit():
                count = int(count_input)
                max_limit = 165 if dataset == "humaneval" else 5
                if 0 < count <= max_limit:
                    return {'type': 'tot', 'value': count}
                else:
                    print(f"❌ Number must be between 1 and {max_limit}.")
            else:
                print("❌ Please enter a valid number.")

        else:
            print("❌ Invalid selection. Enter 1, 2, or 3.")


def check_formatted_data_src_setup():
    try:
        process_humaneval(helper.getPath("humaneval_src"), helper.getPath("humaneval_formatted_data_path"))
        process_refactory(helper.getPath("refactory_src"), helper.getPath("refactory_formatted_data_path"))
    except Exception as e:
        print(f"Error during dataset formatting: {e}")
        exit(9)

if __name__ == '__main__':
    check_formatted_data_src_setup()
    main()