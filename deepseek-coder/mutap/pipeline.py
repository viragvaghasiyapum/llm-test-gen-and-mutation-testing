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

def run_pipeline(limit=None, mode="zero_shot"):
    problems = get_problems()
    if limit:
        problems = problems[:limit]

    allowed_run = 10
    for idx, problem in enumerate(problems):    
        task_id = problem['task_id']
        put_code = problem['code']
        run = 1
        
        print("--------------------------------------------------------------------\n")
        print(f"\n{task_id}: in execution\n")
        print(f"{task_id}: buidling initial prompt")

        initial_prompt = build_prompts(put_code, examples, type=mode)
        helper.save_checkpoint(task_id, run, 'prompts', initial_prompt)

        while allowed_run > 0:
            allowed_run -= 1
            print(f"{task_id}: generating raw test cases")
            raw_initial_unit_test = prompt_deepseek_llmc(initial_prompt)
            helper.save_checkpoint(task_id, run, 'testcases', raw_initial_unit_test)

            print(f"{task_id}: refining raw test cases\n")
            initial_unit_test = refine_test_cases(raw_initial_unit_test, put_code, task_id, run)
            
            if initial_unit_test != False:
                break
        
        if initial_unit_test == False:
            print(f"{task_id}: unable to refine test cases after {10 - allowed_run} attempts, skipping...")
            continue
        test_file_path =format_testcases(
            "\n".join(initial_unit_test),
            task_id,
            run,
            extract_func_name(initial_unit_test[1]).strip() if len(initial_unit_test) > 1 else "TestFunction"
        )
        helper.save_checkpoint(task_id, run, 'refinement', "\n".join(initial_unit_test))

        print(f"{task_id}: mutating task & out for killing mutants (Charles, you better watch out <_>)")
        # test_file_path = helper.getPath('refinement', task_id) + f"/mutpy_testcase_run{run}_{task_id}.py"
        mutation_result = run_mutation_testing(task_id, test_file_path, run)
        
        mutants_survived = int(mutation_result['survived']['total'])
        mutants = mutation_result['survived']['mutants']
        print(f"{task_id}: run_{run} mission report... ")
        print(f"\t mutation_score: {mutation_result ['mutation_score']}")
        print(f"\t total_mutants: {mutation_result['total_mutants']}")
        print(f"\t killed_mutants: {mutation_result['killed']['total']}")
        print(f"\t mutant_survived: {mutants_survived} -> {mutants}")
        print(f"\t total_time: {mutation_result['total_time']}")
        print(f"\n\t {'' if mutants_survived > 0 else '( haha, gotcha charles! x_x )'}")      

        if mutants_survived > 0 :
            if len(mutants) <= 0 :
                print(f"{task_id}: mutants list is empty")
                return
            
            augmented_unit_test = augmentation_process(
                mutants_survived,
                put_code,
                initial_prompt,
                initial_unit_test,
                mutants,
                task_id,
                int(run)
            )
        else:
            augmented_unit_test = initial_unit_test
        
        final_unit_tests = minimize_oracles(task_id, put_code, augmented_unit_test)
        
        print("Final Tests for", task_id)
        print(final_unit_tests)
        print("--------------------------------------------------------------------")