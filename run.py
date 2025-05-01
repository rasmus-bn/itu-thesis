if __name__ == '__main__':
    import os
    from tests.test_19_pygad_example import run_ga as run_aga_test_19
    from tests.test_17_different_worlds import run as run_many_worlds
    import multiprocessing

    print(f"current path: {os.getcwd()}")
    os.chdir(os.path.expanduser('~'))
    print(f"current path: {os.getcwd()}")
    os.makedirs("output", exist_ok=True)
    os.chdir("output")
    print(f"current path: {os.getcwd()}")

    multiprocessing.set_start_method('spawn')
    # run_aga_test_19()
    run_many_worlds()





