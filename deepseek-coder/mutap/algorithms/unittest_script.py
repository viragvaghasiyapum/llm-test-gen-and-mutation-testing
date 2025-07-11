# import subprocess
# import shutil
import os
from mutap.utils.helper import getPath, GCD
from mutap.utils.mutpy_test_file_conversion import format_testcases
import importlib.util
import unittest

def refactory_test_buggy_versions(unit_tests, functions):
    try:
        # Get all buggy files
        buggy_dir = getPath("refactory_buggy_dir", GCD.task_id)
        buggy_files = sorted(
            os.path.splitext(f)[0]  # get filename without extension
            for f in os.listdir(buggy_dir)
            if f.endswith(".py")
        )

        csv_data = []
        csv_row = {'dataset': GCD.dataset, 'task_id': '', 'total_buggy_codes': len(buggy_files), 'killed': 0, 'survived': 0, 'total_testcases': 0}
        for i, buggy_file in enumerate(buggy_files, 1):
            csv_row['total_testcases'] = csv_row['killed'] = csv_row['survived'] = 0
            csv_row['task_id'] = f"{buggy_file}.py"
            test_file_path = format_testcases(
                "\n".join(unit_tests),
                GCD.task_id,
                GCD.run,
                functions,
                buggy_file= buggy_file
            )

            csv_row['total_testcases'] = len(unit_tests)

            spec = importlib.util.spec_from_file_location("test_module", test_file_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)

            # Load and run the tests
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            result = unittest.TextTestRunner(verbosity=2).run(suite)

            # Summary
            if result.failures or result.errors:
                print("✅ Test caught the bug:")
                for failed_test, traceback in result.failures + result.errors:
                    csv_row['killed'] = 1
                    print(f"\n🔹 Failed Test: {failed_test}\n")
            else:
                csv_row['survived'] = 1
                print("\n❌ Test did NOT catch the bug (All tests passed)\n")

            csv_data.append(csv_row.copy())
        return csv_data
    
    except Exception as e:
        print(f"Error in refactory_test_buggy_versions: {e}")
        exit(70)