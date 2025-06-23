# mutap/algorithms/oracle.py
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.utils import helper
from mutap.utils.mutpy_test_file_conversion import format_testcases, extract_func_name
import os

#lower score doesnt necessarily mean better tests, but it is a good heuristic
# it should be based on which unique mutants it killed

def minimize_oracles(id, test_cases: list) -> list:
    try:
        final_unit_tests = []
        tmp_test_cases = test_cases
        killed_already = []
        for line in tmp_test_cases[1:]:

            tmp_content = "\n".join(test_cases[0:1] + [line])
            test_file_path = format_testcases(
                tmp_content,
                id,
                0,
                extract_func_name(line)
            )

            if not test_file_path:
                print(f"{id}: unable to format test cases for mutpy in orcale minimization, skipping..., check tmp logs for more details.")
                continue

            ms_report = run_mutation_testing(id, test_file_path, run=0, log=False)
            if not ms_report:
                print(f"{id}: unable to minimize oracle, skipping..., check tmp logs for more details.")
                continue
            killed = int(ms_report['killed']['total'])
            killed_mutants = ms_report['killed']['mutants']
            new_kills = [m for m in killed_mutants if m not in killed_already]
            if killed > 0 and len(new_kills) > 0:
                final_unit_tests.append(line)
                killed_already = killed_already + new_kills

        print(f"Final unit tests after minimization: {len(final_unit_tests)}")
        test_dir = helper.getPath('testcases', id)
        with open(os.path.join(test_dir, 'final_tests.py'), 'w') as f:
            f.write("\n".join(test_cases[0:1] + final_unit_tests))

        return final_unit_tests
    except Exception as e:
        helper.writeTmpLog(f"Error (oracle_minimization): issue minimizing oracles for {id} -> {e}", 'test_generation.log')
    return []
