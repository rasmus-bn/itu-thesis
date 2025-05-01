from pygad import pygad

val = 0
all_fitness_per_gen = []


def on_generation(ga_instance):
    all_fitness_per_gen.append(ga_instance.last_generation_fitness.copy())


def fitness_func(instance: pygad.GA, solution, solution_idx):
    global val
    if instance.generations_completed < 15:
        val += 0.1 # improve
    else:
        val -= 0.1 # decline
    return solution[0] + val


def run_ga():
    gene_space = [
        {'low': 0, 'high': 100, 'step': 0.25},
        {'low': 0.0, 'high': 100.0}
    ]

    ga_instance = pygad.GA(
        num_generations=30,
        sol_per_pop=30,
        num_genes=2,
        gene_space=gene_space,
        fitness_func=fitness_func,
        num_parents_mating=2,
        crossover_type=None,
        mutation_type="random",
        parent_selection_type="random",
        mutation_by_replacement=True,
        mutation_percent_genes=100,
        keep_parents=0,
        keep_elitism=0,
        on_generation=on_generation,
        random_mutation_min_val=-100,
        random_mutation_max_val=100,
        save_solutions=True,
    )

    ga_instance.run()
    # ga_instance
    ga_instance.plot_fitness()
    ga_instance.plot_genes()
    ga_instance.plot_new_solution_rate()
    # ga_instance.plot_pareto_front_curve()


    solution, solution_fitness, _ = ga_instance.best_solution()
    print(f"Best solution: {solution} | Best fitness: {solution_fitness}")

    ga_instance.save()


def plot_it():
    # Calculate Statistics
    generations = range(len(all_fitness_per_gen))
    best_fitness_per_gen = [max(fitnesses) for fitnesses in all_fitness_per_gen]
    avg_fitness_per_gen = [sum(fitnesses) / len(fitnesses) for fitnesses in all_fitness_per_gen]
    overall_best_fitness = []
    current_overall_best = float('-inf')
    for best in best_fitness_per_gen:
        current_overall_best = max(current_overall_best, best)
        overall_best_fitness.append(current_overall_best)

    # Plotting
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.boxplot(all_fitness_per_gen, positions=generations, widths=0.6, patch_artist=True, showfliers=False)
    ax.plot(generations, best_fitness_per_gen, label='Best Fitness', marker='o')
    ax.plot(generations, overall_best_fitness, label='Overall Best', linestyle='--')
    ax.plot(generations, avg_fitness_per_gen, label='Average')
    ax.scatter(
        [gen for gen in generations for _ in all_fitness_per_gen[gen]],
        [fitness for gen_fitness in all_fitness_per_gen for fitness in gen_fitness],
        color='red', s=5, alpha=0.6, zorder=2, label='Individual Fitness'
    )

    ax.set_title("Generational Fitness Overview")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    run_ga()
    plot_it()
