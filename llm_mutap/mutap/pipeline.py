from mutap.algorithms.prompting import build_prompts
from mutap.algorithms.test_generation import prompt_llmc
from mutap.algorithms.refinement import refine_test_cases
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.algorithms.augmentation import augmentation_process
from mutap.algorithms.oracle_minimization import minimize_oracles
import mutap.utils.helper as helper
from mutap.utils.loader import get_problems
from mutap.utils.mutpy_test_file_conversion import format_testcases
from mutap.utils.helper import extract_function_name
import time
from mutap.utils.helper import GCD
from mutap.algorithms.unittest_script import refactory_test_buggy_versions

def run_pipeline(limit: dict, prompt_type: str, llm: str, method: str, dataset: str):

    try:
        GCD.reset(full_reset=True)
        helper.cleanOldRunFiles(cleanTemp= True)
        limit_type = limit['type']
        limit_value = limit['value'] 
        GCD.dataset = dataset
        GCD.method = method
        GCD.prompt = prompt_type
        GCD.llm = llm
        problems = []
        if limit_type == 'specific':
            problems = get_problems(dataset, target= str(limit_value))
        else:
            probs = get_problems(dataset)
            problems = probs[:limit_value] if limit_type == 'tot' else probs
            probs = None;

        print(f"Running {len(problems)} tasks with {prompt_type} prompt_type...")

        for idx, problem in enumerate(problems): 
            
            GCD.reset(normal_reset= True)
            initial_test_run = -1
            task_id = problem['task_id']
            GCD.task_id = task_id
            GCD.run = 1
            put_code = problem['code']
            run = 0
            helper.writeTmpLog(f"\n---------------------------------------------\ntask_id: {task_id}.", 'test_generation.log')
            helper.cleanOldRunFiles(id= task_id)
            
            print("--------------------------------------------------------------------\n")
            print(f"\n{task_id}: in execution\n")
            print(f"{task_id}: buidling initial prompt")

            # Promt Generation
            initial_prompt = build_prompts(put_code)
            helper.writeReportLog('initial_prompt.log', 'prompts', 'initial prompt', initial_prompt, task_id, run)

            putcode_functions = extract_function_name(put_code)
            if not putcode_functions:
                print(f"{task_id}: unable to extract function names from put code, skipping...")
                exit(10)
            initial_unit_test = lhs_fixed_initial_unit_test = False

            while initial_test_run < 10:
                
                initial_test_run += 1
                
                print(f"{task_id} -> subrun {initial_test_run}: generating raw test cases")

                # Raw Testcase Generation
                raw_initial_unit_test = prompt_llmc(initial_prompt, putcode_functions)
                helper.writeReportLog('initial_raw_tests.log', 'testcases', 'raw initial unit tests (raw_IUT) with 10 subruns, last successful output will be considered 0th raw initial unit test', raw_initial_unit_test, task_id, initial_test_run)
                if not raw_initial_unit_test:
                    continue
                
                if method == 'before_refining':
                    initial_unit_test = raw_initial_unit_test.strip().splitlines()
                    lhs_fixed_initial_unit_test = initial_unit_test.copy()
                    break
            
                print(f"{task_id} -> subrun {initial_test_run}: refining raw test cases\n")
                
                # Testcase Refinement
                initial_unit_test, lhs_fixed_initial_unit_test = refine_test_cases(raw_initial_unit_test, put_code, putcode_functions, task_id, run)

                if not initial_unit_test:
                    helper.writeReportLog('initial_refined_tests.log', 'testcases', 'refined initial unit tests (IUT) with 10 subruns, last successful output will be considered 0th refined initial unit test', str(initial_unit_test), task_id, initial_test_run)
                    continue
                else:
                    helper.writeReportLog('initial_refined_tests.log', 'testcases', 'refined initial unit tests (IUT) with 10 subruns, last successful output will be considered 0th refined initial unit test', "\n".join(initial_unit_test), task_id, initial_test_run)
                    break
            
            GCD.subrun = initial_test_run
            if initial_unit_test in [False, None, []]:
                print(f"{task_id}: unable to generate initial test cases after {initial_test_run} attempts, skipping..., check tmp logs for more details.")
                GCD.problematic_put = 1
                helper.write_mutap_analysis()
                if GCD.dataset == 'refactory':
                    execute_buggy_run([], [])
                continue
            
            if method != 'before_refining':
                GCD.refined_tests = len(initial_unit_test)

            # Format Testcase for Mutpy
            test_file_path = format_testcases(
                "\n".join(initial_unit_test),
                task_id,
                run,
                putcode_functions
            )
            if not test_file_path:
                print(f"{task_id}: unable to format test cases for mutpy, skipping..., check tmp logs for more details.")
                exit(11)
                continue

            print(f"{task_id}: mutating task & out for killing mutants\n\n( Charles, you better watch out... <_> )\n")

            # final_run = True if method != 'mutap' else False
            # Run Mutation Testing
            mutation_result = run_mutation_testing(task_id, test_file_path, putcode_functions, run)
            if not mutation_result:
                print(f"{task_id}: unable to generate initial mutants, skipping..., check tmp logs for more details.")
                GCD.problematic_put = 1
                helper.write_mutap_analysis()
                if GCD.dataset == 'refactory':
                    execute_buggy_run([], [])    
                continue

            mutants_survived = int(mutation_result['survived']['total'])
            mutants = mutation_result['survived']['mutants']
            print(f"{task_id}: run_{run} mission report... ")
            print(f"\t mutation_score: {mutation_result ['mutation_score']}")
            print(f"\t total_mutants: {mutation_result['total_mutants']}")
            print(f"\t killed_mutants: {mutation_result['killed']['total']}")
            print(f"\t mutant_survived: {mutants_survived} -> {mutants}")
            print(f"\t mutation_testing_time: {mutation_result['total_time']}")
            if mutants_survived <= 0:
                print("\n\t( haha, gotcha Charles!... x_x )\n")      

            augmented_unit_test = []
            if mutants_survived > 0 and method == 'mutap':
                if len(mutants) <= 0 :
                    print(f"{task_id}: mutants list is empty")
                    return
                
                # Testcase Augmentation Process
                augmented_unit_test = augmentation_process(
                    mutants_survived,
                    put_code,
                    initial_prompt,
                    initial_unit_test,
                    lhs_fixed_initial_unit_test,
                    mutants,
                    putcode_functions,
                    task_id,
                    int(run)
                )
                if not augmented_unit_test:
                    print(f"{task_id}: unable to generate augmented unit tests, skipping..., check tmp logs for more details.")
                    exit(12)
                    continue
            else:
                augmented_unit_test = initial_unit_test.copy()
            
            if (dataset == 'refactory'):
                execute_buggy_run(augmented_unit_test.copy(), putcode_functions.copy())

            # Minimize Oracles
            if method != 'before_refining':
                print(f"{task_id}: minimizing oracles")
                final_unit_tests = minimize_oracles(task_id, putcode_functions, augmented_unit_test)
            else:
                final_unit_tests = augmented_unit_test
            
            GCD.final_tests = "\n".join(final_unit_tests) if isinstance(final_unit_tests, list) else str(final_unit_tests)
            print("Final Tests for", task_id)
            print(final_unit_tests)
            helper.write_mutap_analysis()
            print("--------------------------------------------------------------------")
            time.sleep(10)  # Sleep to avoid overwhelming the system

    except Exception as e:
        print('Error running pipeline:', e)

    
def execute_buggy_run(unit_tests, functions):
    try:
        data = refactory_test_buggy_versions(unit_tests, functions)
        helper.write_buggy_code_run_analysis(data)
    except Exception as e:
        print(f"Error in execute_buggy_run: {e}")
        helper.writeTmpLog(f"Error in execute_buggy_run: {e}", 'test_generation.log')
        exit(13)