import os
import importlib.util
import unittest
import multiprocessing
from mutap.utils.helper import getPath, GCD
from mutap.utils.mutpy_test_file_conversion import format_testcases
import mutap.utils.helper as helper

def run_tests_with_timeout(test_module_path, timeout=10, report_file='123.log'):
    def run_tests(queue):

        try:
            spec = importlib.util.spec_from_file_location("test_module", test_module_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)

            suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
            result = unittest.TextTestRunner(verbosity=0).run(suite)

            helper.write_buggy_report(f"\n\nfailures : {result.failures}", report_file)
            helper.write_buggy_report(f"\n\nerrors : {result.errors}\n", report_file)

            if result.failures or result.errors:
                print("✅ Test caught the bug:")
                for test_case, tb in result.failures + result.errors:
                    print(f"    ❗ {test_case.id()} => {tb.strip().splitlines()[-1]}")
                queue.put("fail")
            else:
                queue.put("pass")

        except Exception as e:
            print(f"⚠️ Exception during test execution: {type(e).__name__}")
            exit(73)
            queue.put("error")

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_tests, args=(queue,))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return "timeout"

    return queue.get() if not queue.empty() else "error"

def refactory_test_buggy_versions(unit_tests, functions):
    try:
        # Get all buggy files
        buggy_dir = getPath("refactory_buggy_dir", GCD.task_id)
        buggy_files = sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(buggy_dir)
            if f.endswith(".py")
        )

        csv_data = []
        csv_row = {
            'question_id': GCD.task_id,
            'task_id': '',
            'dataset': GCD.dataset,
            'method': GCD.method,
            'llm': GCD.llm,
            'total_buggy_codes': len(buggy_files),
            'killed': 0,
            'survived': 0,
            'total_testcases': len(unit_tests),
            'timeout': 0
        }

        for buggy_file in buggy_files:
            csv_row['killed'] = csv_row['timeout'] = csv_row['survived'] = 0
            csv_row['task_id'] = f"{buggy_file}.py"
            
            report_file = f"{buggy_file}_run_report.log"
            helper.write_buggy_report(f"\n\n##################################################\n method:{GCD.method}, llm: {GCD.llm}\n##################################################\n", report_file)

            if not unit_tests:
                csv_data.append(csv_row.copy())
                helper.write_buggy_report("no test cases\n", report_file)
                continue

            test_file_path = format_testcases(
                "\n".join(unit_tests),
                GCD.task_id,
                GCD.run,
                functions,
                buggy_file=buggy_file
            )

            if not test_file_path:
                print(f"{GCD.task_id}: unable to format test cases for buggy run, skipping...")
                exit(71)

            test_result = run_tests_with_timeout(test_file_path, timeout=60, report_file=report_file)

            if test_result in ["fail", "timeout"]:
                print("✅ Test caught the bug")
                if test_result == "timeout":
                    helper.write_buggy_report(f"\ntimeout case\n", report_file)
                    csv_row['timeout'] = 1
                    print("⏱️ Execution timed out (likely infinite loop)")
                else:
                    csv_row['killed'] = 1
            elif test_result == "pass":
                helper.write_buggy_report(f"\nsurvived\n", report_file)
                csv_row['survived'] = 1
                print("\n❌ Test did NOT catch the bug (All tests passed)\n")
            else:
                print("⚠️ Test execution failed unexpectedly")
                exit(72)

            csv_data.append(csv_row.copy())
        return csv_data

    except Exception as e:
        print(f"Error in refactory_test_buggy_versions: {e}")
        exit(70)