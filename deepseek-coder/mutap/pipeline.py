# mutap/algorithms/pipeline.py
from mutap.algorithms.prompting import build_prompts
from mutap.algorithms.test_generation import prompt_deepseek_llmc
from mutap.algorithms.refinement import refine_test_cases
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.algorithms.augmentation import augmentation_process
from mutap.algorithms.oracle_minimization import minimize_oracles
import mutap.utils.helper as helper
from mutap.utils.loader import get_problems
from data.humaneval.few_shot_examples import examples
from mutap.utils.mutpy_test_file_conversion import format_testcases
from mutap.utils.mutpy_test_file_conversion import extract_func_name
import time

def run_pipeline(limit=None, mode="zero_shot"):
    
    helper.cleanOldRunFiles(cleanTemp= True)
    problems = get_problems()
    if limit:
        problems = problems[:limit]

    initial_test_run = -1
    for idx, problem in enumerate(problems):    
        task_id = problem['task_id']
        put_code = problem['code']
        run = 0

        helper.cleanOldRunFiles(id= task_id)
        
        print("--------------------------------------------------------------------\n")
        print(f"\n{task_id}: in execution\n")
        print(f"{task_id}: buidling initial prompt")

        initial_prompt = build_prompts(put_code, examples, type=mode)
        helper.writeReportLog('initial_prompt.log', 'prompts', 'initial prompt', initial_prompt, task_id, run)

        initial_unit_test = False
        while initial_test_run < 10:
            initial_test_run += 1
            print(f"{task_id} -> subrun {initial_test_run}: generating raw test cases")
            raw_initial_unit_test = prompt_deepseek_llmc(initial_prompt)
            helper.writeReportLog('initial_raw_tests.log', 'testcases', 'raw initial unit tests (raw_IUT) with 10 subruns, last successful output will be considered 0th raw initial unit test', raw_initial_unit_test, task_id, initial_test_run)
            if not raw_initial_unit_test:
                continue

            print(f"{task_id} -> subrun {initial_test_run}: refining raw test cases\n")
            initial_unit_test = refine_test_cases(raw_initial_unit_test, put_code, task_id, run)
            if not initial_unit_test:
                helper.writeReportLog('initial_refined_tests.log', 'testcases', 'refined initial unit tests (IUT) with 10 subruns, last successful output will be considered 0th refined initial unit test', initial_unit_test, task_id, initial_test_run)
            else:
                helper.writeReportLog('initial_refined_tests.log', 'testcases', 'refined initial unit tests (IUT) with 10 subruns, last successful output will be considered 0th refined initial unit test', "\n".join(initial_unit_test), task_id, initial_test_run)
                break
    
        if initial_unit_test == False:
            print(f"{task_id}: unable to generate initial test cases after {initial_test_run} attempts, skipping..., check tmp logs for more details.")
            continue

        test_file_path = format_testcases(
            "\n".join(initial_unit_test),
            task_id,
            run,
            extract_func_name(initial_unit_test[1]).strip() if len(initial_unit_test) > 1 else "TestFunction"
        )

        if not test_file_path:
            print(f"{task_id}: unable to format test cases for mutpy, skipping..., check tmp logs for more details.")
            continue

        print(f"{task_id}: mutating task & out for killing mutants (Charles, you better watch out <_>)")
        mutation_result = run_mutation_testing(task_id, test_file_path, run)
        
        if not mutation_result:
            print(f"{task_id}: unable to generate initial mutants, skipping..., check tmp logs for more details.")
            continue

        mutants_survived = int(mutation_result['survived']['total'])
        mutants = mutation_result['survived']['mutants']
        print(f"{task_id}: run_{run} mission report... ")
        print(f"\t mutation_score: {mutation_result ['mutation_score']}")
        print(f"\t total_mutants: {mutation_result['total_mutants']}")
        print(f"\t killed_mutants: {mutation_result['killed']['total']}")
        print(f"\t mutant_survived: {mutants_survived} -> {mutants}")
        print(f"\t mutation_testing_time: {mutation_result['total_time']}")
        print(f"\n\t {'' if mutants_survived > 0 else '( haha, gotcha charles! x_x )'}")      

        if mutants_survived > 0 :
            if len(mutants) <= 0 :
                print(f"{task_id}: mutants list is empty")
                return
            
            augmented_unit_test = augmentation_process(
                mutants_survived,
                put_code,
                initial_unit_test,
                mutants,
                task_id,
                int(run)
            )
            if not augmentation_process:
                print(f"{task_id}: unable to generate augmented unit tests, skipping..., check tmp logs for more details.")
                continue
        else:
            augmented_unit_test = initial_unit_test
        
        final_unit_tests = minimize_oracles(task_id, augmented_unit_test)
        
        print("Final Tests for", task_id)
        print(final_unit_tests)
        print("--------------------------------------------------------------------")
        time.sleep(10)  # Sleep to avoid overwhelming the output