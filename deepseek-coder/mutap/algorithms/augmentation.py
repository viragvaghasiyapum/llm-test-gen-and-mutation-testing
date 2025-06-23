from mutap.algorithms.test_generation import prompt_deepseek_llmc
from mutap.algorithms.refinement import refine_test_cases
from mutap.algorithms.mutation_testing import run_mutation_testing
import mutap.utils.helper as helper
from data.humaneval.few_shot_examples import examples
import os 
from mutap.utils.mutpy_test_file_conversion import format_testcases
from mutap.utils.mutpy_test_file_conversion import extract_func_name

def augmentation_process(mutants_survived: int, put_code: str,
                         initial_unit_test: list, mutants: list, task_id: str, run: int) -> list:

    # Base initialization
    current_test_suite = initial_unit_test
    #  {mutants}  wont matter further as mutpy regenerates mutants and there might be difference in order
    surving_mutants = mutants

    try:
        allowed_run = 1
        while mutants_survived > 0 and len(surving_mutants) > 0 and allowed_run <= 10:
            run += 1
            mutant_code = ""
            mutant_dir = helper.getPath('mutants', task_id)
            mutant_file = os.path.join(mutant_dir, surving_mutants.pop())
            with open(mutant_file, 'r') as f:
                mutant_code = f.read()

            # Augment prompt
            ins3 = "\n# FAULTY code:"
            ins4 = """\n#generate NEW assert-based unit tests\n# test case:\n<test>\ndef test():\n    assert"""
            augmented_prompt = f"{ins3}\n<code>\n{mutant_code}\n</code>\n{ins4}"
            helper.writeReportLog('augmented_prompt.log', 'prompts', 'augmented prompts', augmented_prompt, task_id, allowed_run)

            raw_aug_unit_test = prompt_deepseek_llmc(augmented_prompt)
            helper.writeReportLog('raw_augmented_tests.log', 'testcases', 'raw augmented unit tests', raw_aug_unit_test, task_id, allowed_run)
            
            if not raw_aug_unit_test:
                print(f"{task_id} aug_run {allowed_run}: unable to generate raw augmented test cases, skipping... check tmp logs for more details.")
                continue

            aug_unit_test = refine_test_cases(raw_aug_unit_test, put_code, task_id, allowed_run)
            if not aug_unit_test:
                print(f"{task_id} aug_run {allowed_run}: unable to generate augmented test cases, skipping... check tmp logs for more details.")
                continue
            aug_unit_test = current_test_suite + aug_unit_test[1:]
            aug_unit_test = list(dict.fromkeys(aug_unit_test))
            helper.writeReportLog('refined_augmented_tests.log', 'testcases', 'refined augmented unit tests', "\n".join(aug_unit_test), task_id, allowed_run)
        
            test_file_path = format_testcases(
                "\n".join(aug_unit_test),
                task_id,
                allowed_run,
                extract_func_name(current_test_suite[1]).strip() if len(current_test_suite) > 1 else "TestFunction"
            )
            if not test_file_path:
                print(f"{task_id}: unable to format test cases for mutpy, skipping..., check tmp logs for more details.")
                continue

            current_test_suite = aug_unit_test
            mutation_result = run_mutation_testing(task_id, test_file_path, allowed_run)
            if not mutation_result:
                print(f"{task_id}: unable to generate mutants in augmentation, skipping..., check tmp logs for more details.")
                continue
            mutants_survived = int(mutation_result['survived']['total'])
            mutants = mutation_result['survived']['mutants']
            print(f"\n{task_id}: run_{allowed_run} mission report... ")
            print(f"\t mutation_score: {mutation_result ['mutation_score']}")
            print(f"\t mutant_survived: {mutation_result['total_mutants']}")
            print(f"\t mutant_survived: {mutation_result['killed']['total']}")
            print(f"\t mutant_survived: {mutants_survived} -> {mutants}")
            print(f"\t mutant_survived: {mutation_result['total_time']}")
            print(f"\n\t {'' if mutants_survived > 0 else '( haha, gotcha charles! x_x )'}")
        
            surving_mutants = mutants
            allowed_run += 1

        if len(surving_mutants) > 0:
            print("\n( Charles, you got away this time... -_- )")
        return current_test_suite
    except Exception as e:
        helper.writeTmpLog(f"\n Error (augmentation): issue augmenting testcases and mutation testing -> {e}", 'test_generation.log')
    return False


 