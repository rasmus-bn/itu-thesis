if __name__ == '__main__':
    import os
    from tests.test_19_pygad_example import run_ga as run_ga_test_19
    from tests.test_17_different_worlds import run as run_many_worlds
    import multiprocessing
    import sys
    from datetime import datetime

    # First argument is the script name
    print("Script name:", sys.argv[0])

    # All arguments after the script name
    print("Arguments:", sys.argv[1:])

    if len(sys.argv) > 1:
        arg_filename = f"{sys.argv[1]}"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arg_filename = f"unknownJob_{timestamp}"
    arg_test = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"arg_filename: {arg_filename}")
    print(f"arg_other: {arg_test}")

    print(f"current path: {os.getcwd()}")
    # os.chdir(os.path.expanduser('~'))
    # print(f"current path: {os.getcwd()}")
    # os.makedirs("output", exist_ok=True)
    # os.chdir("output")
    # print(f"current path: {os.getcwd()}")
    if sys.platform == 'win32':
        print("running on windows, using spawn")
        multiprocessing.set_start_method('spawn')

    # run_ga_test_19(arg_filename)
    run_many_worlds(arg_filename, test=arg_test)





