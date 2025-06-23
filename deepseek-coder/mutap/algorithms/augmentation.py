from mutap.algorithms.test_generation import prompt_deepseek_llmc
from mutap.algorithms.refinement import refine_test_cases
from mutap.algorithms.mutation_testing import run_mutation_testing
import mutap.utils.helper as helper
from data.humaneval.few_shot_examples import examples
import os 
from mutap.utils.mutpy_test_file_conversion import format_testcases
from mutap.utils.mutpy_test_file_conversion import extract_func_name

def augmentation_process(mutants_survived: int, put_code: str, initial_prompt: str,
                         initial_unit_test: list, mutants: list, task_id: str, run: int) -> list:

    # Base initialization
    current_test_suite = initial_unit_test
    #  {mutants}  wont matter further as mutpy regenerates mutants and there might be difference in order
    surving_mutants = mutants

    allowed_run = 10
    while mutants_survived > 0 and len(surving_mutants) > 0 and allowed_run > 0:
        run += 1
        mutant_code = ""
        mutant_dir = helper.getPath('mutants', task_id)
        mutant_file = os.path.join(mutant_dir, surving_mutants.pop())
        with open(mutant_file, 'r') as f:
            mutant_code = f.read()
        
        # test = '\n'.join(test[1:])
        # TODO: remove duplicate test cases then each mutant 10 run and then oracle minimization
        # TODO: remove prompt generation if not using previous test cases

        # Augment prompt
        ins3 = "\n# FAULTY code:"
        # ins2 = f"\n <incorrect>\n{test}\n</incorrect>\n"
        ins4 = """\n#generate NEW assert-based unit tests\n# test case:\n<test>\ndef test():\n    assert"""
        augmented_prompt = f"{ins3}\n<code>\n{mutant_code}\n</code>\n{ins4}"
        helper.save_checkpoint(task_id, run, 'prompts', augmented_prompt)

        raw_aug_unit_test = prompt_deepseek_llmc(augmented_prompt)
        helper.save_checkpoint(task_id, run, 'testcases', raw_aug_unit_test)
        
        aug_unit_test = refine_test_cases(raw_aug_unit_test, put_code, task_id, run)
        aug_unit_test = current_test_suite + aug_unit_test[1:]
        aug_unit_test = list(dict.fromkeys(aug_unit_test))
        helper.save_checkpoint(task_id, run, 'refinement', "\n".join(aug_unit_test))

        test_file_path = format_testcases(
            "\n".join(aug_unit_test),
            task_id,
            run,
            extract_func_name(current_test_suite[1]).strip() if len(current_test_suite) > 1 else "TestFunction"
        )
        current_test_suite = aug_unit_test

        mutation_result = run_mutation_testing(task_id, test_file_path, run)
        mutants_survived = int(mutation_result['survived']['total'])
        mutants = mutation_result['survived']['mutants']
        print(f"\n\n{task_id}: run_{run} mission report... ")
        print(f"\t mutation_score: {mutation_result ['mutation_score']}")
        print(f"\t mutant_survived: {mutation_result['total_mutants']}")
        print(f"\t mutant_survived: {mutation_result['killed']['total']}")
        print(f"\t mutant_survived: {mutants_survived} -> {mutants}")
        print(f"\t mutant_survived: {mutation_result['total_time']}")
        print(f"\n\t {'' if mutants_survived > 0 else '( haha, gotcha charles! x_x )'}")
    
        surving_mutants = mutants
        allowed_run -= 1

    if len(surving_mutants) > 0:
        print("\n( Charles, you got away this time... -_- )")
    return current_test_suite

 