import pygad


# Replace this with your actual simulation function
def run_simulation(motor_size, battery_size):
    return -(motor_size - 5)**2 - (battery_size - 10)**2 + 100

# Updated fitness function with correct signature
def fitness_func(ga_instance, solution, solution_idx):
    motor_size, battery_size = solution
    return run_simulation(motor_size, battery_size)


def on_generation(ga_instance: pygad.GA):
    print(ga_instance.generations_completed)


gene_space = [
    {'low': 0.1, 'high': 10.0},   # motor_size
    {'low': 1.0, 'high': 100.0}   # battery_size
]

ga_instance = pygad.GA(
    num_generations=10,
    num_parents_mating=5,
    fitness_func=fitness_func,
    sol_per_pop=16,
    num_genes=2,
    gene_space=gene_space,
    mutation_type="random",
    mutation_num_genes=1,
    crossover_type="single_point",
    keep_parents=2,
    on_generation=on_generation
)

# Visualize fitness during the GA process
ga_instance.run()

# Plot fitness after the run


solution, solution_fitness, _ = ga_instance.best_solution()
print("Best solution (motor_size, battery_size):", solution)
print("Best fitness (score):", solution_fitness)
