import os
import subprocess
import argparse

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Run tests for the solution.")
    args.add_argument("--solution", type=str, default="solution.py", help="Path to the solution file.")
    program_to_test  = args.parse_args()
    
    tests = os.listdir("./test-cases")
    for test in tests:
        if test.endswith(".in"):
            test_name = test[:-3]
            print(f"Running test: {test_name}")
            input_file = f"./test-cases/{test_name}.in"
            expected_output_file = f"./solutions/{test_name}.out"
            actual_output_file = f"./test-cases/{test_name}.out"

            with open(input_file, "r") as infile, open(actual_output_file, "w") as outfile:
                subprocess.run(["python", program_to_test.solution], stdin=infile, stdout=outfile, timeout=2)

            with open(expected_output_file, "r") as expected_file, open(actual_output_file, "r") as actual_file:
                expected_output = expected_file.read().strip()
                actual_output = actual_file.read().strip()

                if expected_output == actual_output:
                    print(f"Test {test_name} passed.")
                else:
                    print(f"Test {test_name} failed.")
                    for line_num, (expected_line, actual_line) in enumerate(zip(expected_output.splitlines(), actual_output.splitlines()), start=1):
                        if expected_line != actual_line:
                            print(f"Line {line_num}: {(open(input_file, "r").read().strip().split("\n")[-1])} \tExpected: {expected_line} \tActual: {actual_line}")
                            break