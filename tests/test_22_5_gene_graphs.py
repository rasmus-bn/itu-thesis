from pygad import pygad

from evolutionary.Plotter import Plotter

val = 0


def fitness_func(instance: pygad.GA, solution, solution_idx):
    global val
    if instance.generations_completed < 5:
        val += 0.01  # improve
    else:
        val -= 0.01  # decline
    return val - abs(solution[0] - 0.3) - abs(solution[1] - 0.4) - abs(solution[2] - 0.5) - abs(solution[3] - 0.6) - abs(solution[4] - 0.7)


def run_ga(filename: str):
    plotter = Plotter(filename)

    gene_space = [
        {'low': 0.03, 'high': 1.0},    # colony_agent_count range in normalized range 0-1 e.g. 1.0 = 100
        {'low': 0.0,  'high': 1.0},    # role_a_count_ratio 0.0 - 1.0 both included ( already constrained by 1 robot per role requirement )
        {'low': 0.01, 'high': 0.99},   # role_a_mass_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a role to have robot(s) with 0 weight )
        {'low': 0.01, 'high': 0.99},   # role_a_motor_weight_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a robot without a batter or a motor )
        {'low': 0.01, 'high': 0.99},   # role_b_motor_weight_ratio - same as role_a_motor_weight_ratio
    ]

    ga_instance = pygad.GA(
        num_generations=15,
        num_parents_mating=10,
        fitness_func=fitness_func,
        sol_per_pop=30,
        num_genes=5,
        gene_space=gene_space,
        mutation_type="random",
        mutation_num_genes=1,
        mutation_probability=0.2,
        crossover_type="uniform",
        keep_parents=6,
        on_generation=plotter.on_generation,
        on_parents=plotter.on_parents,
        # parallel_processing=['process', 30],
        # keep_parents=0,
        # keep_elitism=0,
        # mutation_by_replacement=True,
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
