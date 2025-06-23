# mutap/algorithms/oracle.py
from mutap.algorithms.mutation_testing import run_mutation_testing
from mutap.utils import helper
from mutap.utils.mutpy_test_file_conversion import format_testcases, extract_func_name

#lower score doesnt necessarily mean better tests, but it is a good heuristic
# it should be based on which unique mutants it killed

def minimize_oracles(id, put_code: str, test_cases: list) -> list:
    final_unit_tests = []
    tmp_test_cases = test_cases
    killed_already = []
    for line in tmp_test_cases[1:]:

        tmp_content = "\n".join(test_cases[0:1] + [line])
        print(tmp_content)
        test_file_path = format_testcases(
            tmp_content,
            id,
            0,
            extract_func_name(line)
        )
        print("\n\n")
        print(killed_already)

        ms_report = run_mutation_testing(id, test_file_path, run=0)
        killed = int(ms_report['killed']['total'])
        killed_mutants = ms_report['killed']['mutants']
        new_kills = [m for m in killed_mutants if m not in killed_already]
        if killed > 0 and len(new_kills) > 0:
            final_unit_tests.append(line)
            killed_already = killed_already + new_kills
    print(f"Final unit tests after minimization: {len(final_unit_tests)}")
    print(final_unit_tests)
    return final_unit_tests
