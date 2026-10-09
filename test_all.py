import argparse
import os
import subprocess

# Forgot to add, a note here
# This is written like this because I'm on windows and pipe operators work like s**t so I needed a decent way to run them all
# It could be easily be done with .sh or way less lines of python but this is pretty nice
# I wante4d to add support for .kt but compiling kotlin is out of teh scope of this exercise and i don'te really want to do it outside of intellij

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Run tests for the solution.")
    args.add_argument(
        "--solution", type=str, default="solution.py", help="Path to the solution file."
    )
    program_to_test = args.parse_args()

    tests = os.listdir("./test-cases")
    for test in tests:
        if test.endswith(".in"):
            test_name = test[:-3]
            print(f"Running test: {test_name}")
            input_file = f"./test-cases/{test_name}.in"
            expected_output_file = f"./solutions/{test_name}.out"
            actual_output_file = f"./test-cases/{test_name}.out"

            with (
                open(input_file, "r") as infile,
                open(actual_output_file, "w") as outfile,
            ):
                subprocess.run(
                    ["python", program_to_test.solution],
                    stdin=infile,
                    stdout=outfile,
                    timeout=2,
                    check=True,
                )

            with (
                open(expected_output_file, "r") as expected_file,
                open(actual_output_file, "r") as actual_file,
            ):
                expected_output = expected_file.read().strip()
                actual_output = actual_file.read().strip()

                if expected_output == actual_output:
                    print(f"Test {test_name} passed.")
                else:
                    print(f"Test {test_name} failed.")
                    for line_num, (expected_line, actual_line) in enumerate(
                        zip(expected_output.splitlines(), actual_output.splitlines()),
                        start=1,
                    ):
                        if expected_line != actual_line:
                            with open(input_file, "r") as infile:
                                print(
                                    f"Line {line_num}: {(infile.read().strip().split('\n')[-1])} \tExpected: {expected_line} \tActual: {actual_line}"
                                )
                                break
