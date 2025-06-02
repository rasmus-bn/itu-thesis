from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np


def plot_normality_dual(data1, data2, label1="Data 1", label2="Data 2"):
    data1 = np.array(data1)
    data2 = np.array(data2)

    # Basic stats
    mean1, std1 = np.mean(data1), np.std(data1)
    mean2, std2 = np.mean(data2), np.std(data2)

    # Welch's t-test
    t_stat, p_value = stats.ttest_ind(data1, data2, equal_var=False)

    print(p_value)
    print(p_value)

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    # Histogram for data1
    ax = axes[0, 0]
    ax.hist(data1, bins=20, density=True, alpha=0.6, edgecolor='black')
    x1 = np.linspace(min(data1), max(data1), 100)
    ax.plot(x1, stats.norm.pdf(x1, mean1, std1), 'r--', linewidth=2, label='Normal PDF')
    ax.set_title(f"Histogram: {label1}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.grid(True)
    ax.legend()

    # Histogram for data2
    ax = axes[0, 1]
    ax.hist(data2, bins=20, density=True, alpha=0.6, edgecolor='black')
    x2 = np.linspace(min(data2), max(data2), 100)
    ax.plot(x2, stats.norm.pdf(x2, mean2, std2), 'r--', linewidth=2, label='Normal PDF')
    ax.set_title(f"Histogram: {label2}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.grid(True)
    ax.legend()

    # Q-Q plot for data1
    ax = axes[1, 0]
    stats.probplot(data1, dist="norm", plot=ax)
    ax.set_title(f"Q-Q Plot: {label1}")
    ax.grid(True)

    # Q-Q plot for data2
    ax = axes[1, 1]
    stats.probplot(data2, dist="norm", plot=ax)
    ax.set_title(f"Q-Q Plot: {label2}")
    ax.grid(True)

    # Human-readable interpretation of p-value
    if p_value < 0.001:
        p_text = "Very strong evidence of a difference"
    elif p_value < 0.01:
        p_text = "Strong evidence of a difference"
    elif p_value < 0.05:
        p_text = "Moderate evidence of a difference"
    elif p_value < 0.1:
        p_text = "Weak evidence of a difference"
    else:
        p_text = "No evidence of a difference"

    # Add t-test summary as figure text
    summary_text = (
        f"Welch's t-test:\n"
        f"t-statistic = {t_stat:.3f}\n"
        f"p-value     = {p_value:.4f}\n"
        f"Interpretation: {p_text}\n"
        f"{label1} mean = {mean1:.3f}\n"
        f"{label2} mean = {mean2:.3f}"
    )
    fig.text(0.5, 0.8, summary_text, ha='center', va='bottom', fontsize=10,
             bbox=dict(facecolor='white', edgecolor='black'))

    plt.tight_layout(rect=[0, 0, 1, 0.8])  # Leaves more bottom margin
    plt.show()


def test_1():
    fitness_homo = [33.0, 35.0, 36.0, 39.0, 34.0, 32.0, 34.0, 36.0, 38.0, 32.0, 35.0, 33.0, 36.0, 35.0, 29.0, 33.0, 34.0, 35.0, 38.0, 35.0, 34.0, 39.0, 36.0, 34.0, 41.0, 37.0, 34.0, 32.0, 32.0, 31.0, 35.0, 34.0, 35.0, 32.0, 38.0, 39.0,
                    36.0, 40.0, 37.0, 37.0, 32.0, 36.0, 36.0, 38.0, 34.0, 38.0, 35.0, 31.0, 37.0, 33.0, 40.0, 29.0, 35.0, 31.0, 31.0, 36.0, 36.0, 34.0, 40.0, 34.0, 35.0, 26.0, 40.0, 39.0, 36.0, 33.0, 40.0, 33.0, 36.0, 36.0, 36.0, 33.0,
                    32.0, 34.0, 35.0, 41.0, 28.0, 39.0, 35.0, 33.0, 36.0, 35.0, 34.0, 31.0, 37.0, 37.0, 32.0, 33.0, 33.0, 37.0, 33.0, 36.0, 34.0, 29.0, 37.0, 40.0, 28.0, 31.0, 33.0, 26.0, 37.0, 30.0, 34.0, 30.0, 37.0, 41.0, 30.0, 36.0,
                    33.0, 34.0, 38.0, 36.0, 39.0, 40.0, 34.0, 35.0, 38.0, 35.0, 37.0, 36.0]
    fitness_hetero = [32.0, 36.0, 34.0, 42.0, 33.0, 36.0, 42.0, 35.0, 36.0, 35.0, 35.0, 36.0, 40.0, 37.0, 32.0, 43.0, 37.0, 35.0, 35.0, 40.0, 37.0, 39.0, 39.0, 36.0, 39.0, 40.0, 36.0, 36.0, 34.0, 32.0, 40.0, 35.0, 39.0, 41.0, 34.0, 35.0,
                      40.0, 33.0, 35.0, 44.0, 43.0, 33.0, 35.0, 36.0, 33.0, 38.0, 43.0, 35.0, 36.0, 37.0, 35.0, 39.0, 38.0, 37.0, 37.0, 41.0, 33.0, 36.0, 45.0, 31.0, 40.0, 37.0, 39.0, 39.0, 37.0, 36.0, 39.0, 33.0, 34.0, 40.0, 36.0, 40.0,
                      33.0, 39.0, 38.0, 33.0, 37.0, 41.0, 34.0, 41.0, 40.0, 40.0, 40.0, 40.0, 34.0, 39.0, 33.0, 36.0, 41.0, 37.0, 37.0, 39.0, 43.0, 35.0, 40.0, 36.0, 38.0, 39.0, 31.0, 36.0, 36.0, 33.0, 37.0, 38.0, 40.0, 38.0, 34.0, 38.0,
                      32.0, 37.0, 36.0, 37.0, 44.0, 34.0, 40.0, 40.0, 37.0, 34.0, 29.0, 38.0]

    plot_normality_dual(fitness_hetero, fitness_homo, label1="Fitness (Hetero)", label2="Fitness (Homo)")


def test_2():
    two_roles = [34.0, 31.0, 38.0, 35.0, 38.0, 39.0, 37.0, 35.0, 39.0, 40.0, 38.0, 34.0, 36.0, 39.0, 40.0, 31.0, 38.0, 33.0, 39.0, 39.0, 36.0, 36.0, 40.0, 33.0, 39.0, 34.0, 38.0, 36.0, 38.0, 33.0, 36.0, 39.0, 43.0, 33.0, 38.0, 35.0, 34.0, 35.0, 38.0, 37.0, 30.0, 41.0, 40.0, 40.0, 34.0, 38.0, 32.0, 39.0, 33.0, 37.0, 40.0, 36.0, 33.0, 40.0, 38.0, 41.0, 34.0, 40.0, 36.0, 39.0, 41.0, 35.0, 36.0, 38.0, 39.0, 37.0, 33.0, 37.0, 35.0, 42.0, 37.0, 36.0, 39.0, 43.0, 37.0, 38.0, 33.0, 36.0, 35.0, 39.0, 34.0, 37.0, 38.0, 40.0, 42.0, 36.0, 39.0, 41.0, 40.0, 38.0, 32.0, 38.0, 35.0, 40.0, 33.0, 33.0, 36.0, 41.0, 35.0, 42.0, 36.0, 37.0, 38.0, 42.0, 36.0, 41.0, 37.0, 40.0, 38.0, 38.0, 40.0, 28.0, 41.0, 36.0, 40.0, 36.0, 35.0, 36.0, 34.0, 30.0]
    one_role = [35.0, 37.0, 39.0, 36.0, 36.0, 36.0, 38.0, 37.0, 34.0, 41.0, 39.0, 39.0, 42.0, 37.0, 42.0, 41.0, 40.0, 36.0, 44.0, 40.0, 38.0, 35.0, 36.0, 38.0, 34.0, 35.0, 40.0, 35.0, 35.0, 34.0, 35.0, 39.0, 34.0, 39.0, 37.0, 34.0, 38.0, 40.0, 37.0, 41.0, 37.0, 37.0, 35.0, 38.0, 34.0, 38.0, 36.0, 37.0, 35.0, 36.0, 33.0, 35.0, 39.0, 40.0, 36.0, 38.0, 34.0, 31.0, 37.0, 37.0, 37.0, 39.0, 40.0, 36.0, 47.0, 42.0, 36.0, 38.0, 40.0, 33.0, 42.0, 36.0, 35.0, 37.0, 36.0, 40.0, 36.0, 40.0, 37.0, 32.0, 37.0, 37.0, 37.0, 36.0, 39.0, 35.0, 37.0, 40.0, 34.0, 40.0, 37.0, 39.0, 35.0, 38.0, 36.0, 32.0, 36.0, 37.0, 29.0, 35.0, 43.0, 35.0, 41.0, 37.0, 42.0, 40.0, 38.0, 37.0, 33.0, 37.0, 37.0, 37.0, 34.0, 38.0, 37.0, 37.0, 41.0, 34.0, 37.0, 30.0]
    plot_normality_dual(two_roles, one_role, label1="Fitness (Two Roles)", label2="Fitness (One Role)")


if __name__ == '__main__':
    # test_1()
    test_2()
