from mutap.algorithms.test_generation import prompt_deepseek_llmc
from mutap.algorithms.refinement import refine_test_cases
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.algorithms.prompting import build_prompts
import mutap.utils.helper as helper
import os 
from mutap.utils.mutpy_test_file_conversion import format_testcases
import re
from mutap.utils.helper import GCD

def augmentation_process(mutants_survived: int, put_code: str, initial_prompt: str,
                         initial_unit_test: list, mutants: list, functions: list[str], task_id: str, run: int) -> list:

    # Base initialization
    current_test_suite = initial_unit_test
    #  {mutants}  wont matter further as mutpy regenerates mutants and there might be difference in order
    surving_mutants = mutants

    try:
        allowed_run = 0
        while mutants_survived > 0 and len(surving_mutants) > 0 and allowed_run < 10:
            allowed_run += 1
            GCD.run += 1
            mutant_code = ""
            mutant_dir = helper.getPath('mutants', task_id)
            current_mutant = surving_mutants[-1]  # Get the last mutant in the list
            surving_mutants = surving_mutants[1:] + surving_mutants[:1] # circular left shift in case of errorsome mutant
            mutant_file = os.path.join(mutant_dir, current_mutant)
            with open(mutant_file, 'r') as f:
                mutant_code = f.read()
            
            function_str = ''
            if len(functions) > 1:
                mutated_function = extract_mutated_func_name(mutant_code).strip()
                function_str = " for function: '" + mutated_function + "'"
                mutant_code = '\n'.join(
                    line for line in mutant_code.splitlines()
                    if not line.strip().startswith('# mutated_function_in_mutpy:')
                )

            # Augment prompt
            augmented_prompt = build_prompts(mutant_code, 'augmentation_prompt', function_str, initial_prompt=initial_prompt, unit_tests=current_test_suite)
            helper.writeReportLog('augmented_prompt.log', 'prompts', 'augmented prompts', augmented_prompt, task_id, allowed_run)

            raw_aug_unit_test = prompt_deepseek_llmc(augmented_prompt)
            helper.writeReportLog('raw_augmented_tests.log', 'testcases', 'raw augmented unit tests', raw_aug_unit_test, task_id, allowed_run)

            if not raw_aug_unit_test:
                print(f"\n{task_id} aug_run {allowed_run}: unable to generate raw augmented test cases, skipping... check tmp logs for more details.")
                continue

            aug_unit_test = refine_test_cases(raw_aug_unit_test, put_code, functions, task_id, allowed_run)
            if not aug_unit_test:
                print(f"{task_id} aug_run {allowed_run}: unable to generate augmented test cases, skipping... check tmp logs for more details.")
                continue

            GCD.refined_tests += len(aug_unit_test)
            GCD.duplicate_tests_removed += len(list(set(current_test_suite) & set(aug_unit_test)))
            aug_unit_test = list(dict.fromkeys(current_test_suite + aug_unit_test))
            
            helper.writeReportLog('refined_augmented_tests.log', 'testcases', 'refined augmented unit tests', "\n".join(aug_unit_test), task_id, allowed_run)
        
            test_file_path = format_testcases(
                "\n".join(aug_unit_test),
                task_id,
                allowed_run,
                functions
            )
            if not test_file_path:
                print(f"{task_id}: unable to format test cases for mutpy, skipping..., check tmp logs for more details.")
                continue

            current_test_suite = aug_unit_test
            final_run = True if allowed_run == 10 else False
            mutation_result = run_mutation_testing(task_id, test_file_path, functions, allowed_run, final_run=final_run)
            if not mutation_result:
                print(f"{task_id}: unable to generate mutants in augmentation, skipping..., check tmp logs for more details.")
                continue
            mutants_survived = int(mutation_result['survived']['total'])
            mutants = mutation_result['survived']['mutants']
            print(f"\n{task_id}: run_{allowed_run} mission report... ")
            print(f"\t mutation_score: {mutation_result ['mutation_score']}")
            print(f"\t total_mutants: {mutation_result['total_mutants']}")
            print(f"\t killed: {mutation_result['killed']['total']}")
            print(f"\t survived: {mutants_survived} -> {mutants}")
            print(f"\t mutation_testing_time: {mutation_result['total_time']}")
            if mutants_survived <= 0:
                print("\n\t( haha, gotcha charles!... x_x )\n")
        
            surving_mutants = mutants
            

        if len(surving_mutants) > 0:
            print("\n( You got away this time, Charles... -_- )\n")
        
        return current_test_suite
    except Exception as e:
        helper.writeTmpLog(f"\n Error (augmentation): issue augmenting testcases and mutation testing -> {e}", 'test_generation.log')
    return False


def extract_mutated_func_name(mutant_code: str) -> str:
    try:
        for line in mutant_code.splitlines():
            match = re.search(r'#\s*mutated_function_in_mutpy:\s*\$(.*?)\$', line)
            if match:
                return match.group(1).strip()
    except Exception as e:
        helper.writeTmpLog(f"\n Error (augmentation): issue extracting mutated function name -> {e}", 'test_generation.log')
    return ''