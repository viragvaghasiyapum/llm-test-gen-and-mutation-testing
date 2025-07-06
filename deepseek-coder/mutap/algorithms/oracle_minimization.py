# mutap/algorithms/oracle.py
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.utils import helper
from mutap.utils.mutpy_test_file_conversion import format_testcases, extract_func_name
import os

# lower score doesnt necessarily mean better tests, but it is a good heuristic
# it should be based on which unique mutants it killed

def minimize_oracles(id, functions: list[str], test_cases: list) -> list:
    try:
        test_processing = 1
        oracles = []
        tmp_test_cases = test_cases
        for line in tmp_test_cases:

            # TODO: give this a temp file name
            test_file_path = format_testcases(
                line,
                id,
                test_processing,
                functions
            )

            if not test_file_path:
                print(f"{id}: unable to format test cases for mutpy in orcale minimization, skipping..., check tmp logs for more details.")
                continue

            ms_report = run_mutation_testing(id, test_file_path, functions, test_processing, isOracleRun=True)
            test_processing += 1
            if not ms_report:
                print(f"{id}: unable to minimize oracle, skipping..., check tmp logs for more details.")
                continue
            killed = int(ms_report['killed']['total'])
            killed_mutants = ms_report['killed']['mutants']

            if killed > 0:
                oracles.append({'case': line, 'mutants': killed_mutants})
        
        final_unit_tests = optimize_oracles(oracles)
        test_dir = helper.getPath('testcases', id)
        with open(os.path.join(test_dir, 'final_tests.py'), 'w') as f:
            f.write("\n".join(final_unit_tests))

        return final_unit_tests
    except Exception as e:
        helper.writeTmpLog(f"Error (oracle_minimization): issue minimizing oracles for {id} -> {e}", 'test_generation.log')
    return []


def optimize_oracles(data: list) -> list:
    try: 
        retained = []
        covered = set()

        # Sort oracles by number of mutants descending (optional heuristic)
        sorted_oracles = sorted(data, key=lambda o: -len(o['mutants']))

        for oracle in sorted_oracles:
            unique_mutants = set(oracle['mutants']) - covered
            if unique_mutants:
                retained.append(oracle['case'])
                covered.update(oracle['mutants'])

        return retained
    except Exception as e:
        helper.writeTmpLog(f"Error (optimize_oracles): issue optimizing oracles -> {e}", 'test_generation.log')
        return []