from datetime import datetime
import hashlib
from pygad import pygad

class Plotter:
    def __init__(self):
        self.all_fitness_per_gen = []
        self.all_genes_per_gen = []
        self.all_solution_hashes = []

    @staticmethod
    def hash_individual(individual):
        return hashlib.md5(individual.tobytes()).hexdigest()

    def on_parents(self, ga_instance, selected_parents):
        if ga_instance.generations_completed == 0:
            self.record_population(ga_instance)

    def on_generation(self, ga_instance):
        self.record_population(ga_instance)
        print(f"Generation = {ga_instance.generations_completed}")
        print(f"Best Fitness = {ga_instance.best_solution()}")

    def record_population(self, ga_instance):
        self.all_fitness_per_gen.append(ga_instance.last_generation_fitness.copy())
        self.all_genes_per_gen.append(ga_instance.population.copy())
        current_hashes = {Plotter.hash_individual(ind) for ind in ga_instance.population}
        self.all_solution_hashes.append(current_hashes)

    def plot_fitness(self, filename=None):
        # Calculate Statistics
        generations = range(len(self.all_fitness_per_gen))
        best_fitness_per_gen = [max(fitnesses) for fitnesses in self.all_fitness_per_gen]
        avg_fitness_per_gen = [sum(fitnesses) / len(fitnesses) for fitnesses in self.all_fitness_per_gen]
        overall_best_fitness = []
        current_overall_best = float('-inf')
        for best in best_fitness_per_gen:
            current_overall_best = max(current_overall_best, best)
            overall_best_fitness.append(current_overall_best)

        # Plotting
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.boxplot(self.all_fitness_per_gen, positions=generations, widths=0.6, patch_artist=True, showfliers=False)
        ax.plot(generations, best_fitness_per_gen, label='Best Fitness', marker='o')
        ax.plot(generations, overall_best_fitness, label='Overall Best', linestyle='--')
        ax.plot(generations, avg_fitness_per_gen, label='Average')
        ax.scatter(
            [gen for gen in generations for _ in self.all_fitness_per_gen[gen]],
            [fitness for gen_fitness in self.all_fitness_per_gen for fitness in gen_fitness],
            color='red', s=5, alpha=0.6, zorder=2, label='Individual Fitness'
        )

        ax.set_title("Generational Fitness Overview")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        ax.legend()

        if filename:
            plt.savefig(filename)
        else:
            plt.show()

    def plot_genes(self):
        import matplotlib.pyplot as plt
        num_genes = self.all_genes_per_gen[0].shape[1]

        fig, axs = plt.subplots(num_genes, 1, figsize=(10, 4 * num_genes), sharex=True)
        if num_genes == 1:
            axs = [axs]

        for gene_idx in range(num_genes):
            xs = []
            ys = []
            for gen_idx, pop in enumerate(self.all_genes_per_gen):
                xs.extend([gen_idx] * pop.shape[0])
                ys.extend(pop[:, gene_idx])
            axs[gene_idx].scatter(xs, ys, alpha=0.7, s=25)
            axs[gene_idx].set_title(f"Gene {gene_idx} Values Over Generations")
            axs[gene_idx].set_ylabel("Gene Value")

        axs[-1].set_xlabel("Generation")
        plt.tight_layout()
        plt.show()

    def plot_new_solutions(self):
        import matplotlib.pyplot as plt

        new_counts = []
        for gen_idx in range(1, len(self.all_solution_hashes)):
            prev_gen = self.all_solution_hashes[gen_idx - 1]
            curr_gen = self.all_solution_hashes[gen_idx]
            new_count = sum(1 for h in curr_gen if h not in prev_gen)
            new_counts.append(new_count)

        generations = list(range(1, len(self.all_solution_hashes)))

        plt.figure(figsize=(8, 4))
        plt.plot(generations, new_counts, marker='o')
        plt.title("New Solutions Over Generations")
        plt.xlabel("Generation")
        plt.ylabel("Number of New Solutions")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plot_best_solution(self):
        import matplotlib.pyplot as plt
        import numpy as np

        # Best overall
        max_fitness_all = float('-inf')
        best_solution_all = None
        for gen_idx, gen in enumerate(self.all_fitness_per_gen):
            gen = np.array(gen)
            gen_max = np.max(gen)
            if gen_max > max_fitness_all:
                max_fitness_all = gen_max
                best_gen_index_all = gen_idx
                best_sol_index_all = np.argmax(gen)
                best_solution_all = self.all_genes_per_gen[best_gen_index_all][best_sol_index_all]

        # Best in last generation
        last_gen_idx = len(self.all_fitness_per_gen) - 1
        last_gen_fitness = np.array(self.all_fitness_per_gen[-1])
        last_gen_genes = self.all_genes_per_gen[-1]
        best_sol_index_last = np.argmax(last_gen_fitness)
        best_solution_last = last_gen_genes[best_sol_index_last]
        max_fitness_last = last_gen_fitness[best_sol_index_last]

        # Plotting
        fig, axs = plt.subplots(2, 1, figsize=(5, 3))
        axs[0].axis("off")
        axs[1].axis("off")

        axs[0].text(0, 1, (
            "Best Overall Solution\n"
            f"Generation: {best_gen_index_all}\n"
            f"Genes: {np.round(best_solution_all, 3)}\n"
            f"Fitness: {max_fitness_all:.3f}"
        ), va='top', ha='left', fontsize=12, fontweight='bold', transform=axs[0].transAxes)

        axs[1].text(0, 1, (
            "Best in Last Generation\n"
            f"Generation: {last_gen_idx}\n"
            f"Genes: {np.round(best_solution_last, 3)}\n"
            f"Fitness: {max_fitness_last:.3f}"
        ), va='top', ha='left', fontsize=12, fontweight='bold', transform=axs[1].transAxes)

        plt.tight_layout()
        plt.show()

    def plot_final_generation_table(self):
        import matplotlib.pyplot as plt
        import numpy as np

        # Get final generation population and fitness
        final_gen_genes = self.all_genes_per_gen[-1]
        final_gen_fitness = self.all_fitness_per_gen[-1]

        # Sort by fitness
        combined = list(zip(final_gen_genes, final_gen_fitness))
        combined.sort(key=lambda x: x[1], reverse=True)

        # Transpose table data
        column_labels = [f"#{i}" for i in range(len(combined))]
        row_labels = ["Gene 0", "Gene 1", "Fitness"]
        table_data = [
            [f"{combined[i][0][0]:.2f}" for i in range(len(combined))],  # Gene 0
            [f"{combined[i][0][1]:.2f}" for i in range(len(combined))],  # Gene 1
            [f"{combined[i][1]:.2f}" for i in range(len(combined))],  # Fitness
        ]

        # Plot table
        fig, ax = plt.subplots(figsize=(24, 8))
        ax.axis("off")
        table = ax.table(
            cellText=table_data,
            rowLabels=row_labels,
            colLabels=column_labels,
            loc='center',
            cellLoc='center'
        )
        # table.scale(1.2, 1.2)
        plt.tight_layout()
        plt.show()


val = 0


def fitness_func(instance: pygad.GA, solution, solution_idx):
    global val
    if instance.generations_completed < 5:
        val += 0.1  # improve
    else:
        val -= 0.1  # decline
    return solution[0] + val


def run_ga(plotter: Plotter):
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

    # save
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ga_instance_world{0}_{timestamp}"
    ga_instance.save(filename)

    # ga_instance.plot_fitness()
    # ga_instance.plot_genes()
    # ga_instance.plot_new_solution_rate()

    solution, solution_fitness, _ = ga_instance.best_solution()
    print(f"Best solution: {solution} | Best fitness: {solution_fitness}")


if __name__ == "__main__":
    plotter = Plotter()
    run_ga(plotter)
    plotter.plot_fitness()
    # plotter.plot_genes()
    # plotter.plot_new_solutions()
    plotter.plot_best_solution()
    # plotter.plot_final_generation_table()
