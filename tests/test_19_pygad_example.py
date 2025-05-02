from pygad import pygad

from evolutionary.Plotter import Plotter

val = 0


def fitness_func(instance: pygad.GA, solution, solution_idx):
    global val
    if instance.generations_completed < 5:
        val += 0.1  # improve
    else:
        val -= 0.1  # decline
    return solution[0] + val


def run_ga(filename: str):
    plotter = Plotter(filename)

    gene_space = [
        {'low': 0, 'high': 100, 'step': 1},
        {'low': 0.0, 'high': 100.0}
    ]

    ga_instance = pygad.GA(
        num_generations=10,
        sol_per_pop=30,
        num_genes=2,
        gene_space=gene_space,
        fitness_func=fitness_func,
        num_parents_mating=30,
        crossover_type="uniform",
        mutation_type="random",
        parent_selection_type="random",
        # mutation_by_replacement=True,
        mutation_num_genes=1,
        mutation_probability=0.1,
        keep_parents=1,
        keep_elitism=0,
        on_generation=plotter.on_generation,
        on_parents=plotter.on_parents,
        # save_solutions=True,
        # parallel_processing=['process', 4],
    )

    # run
    ga_instance.run()

    # save result
    plotter.plot_all()
    plotter.plot_all_default(ga_instance)
    plotter.save_all(ga_instance)

    # print best solution
    solution, solution_fitness, _ = ga_instance.best_solution()
    print(f"Best solution: {solution} | Best fitness: {solution_fitness}")


if __name__ == "__main__":
    run_ga("test")
