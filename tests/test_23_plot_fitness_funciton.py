import matplotlib.pyplot as plt

# Define collected resources and completed times
collected_resources = list(range(0, 6)) + [5]*6
completed_time = [60] * 6 + [60 * 0.6**i for i in range(1, 7)]

# Calculate fitness values
fitness = [60 / t * c for c, t in zip(collected_resources, completed_time)]

# Print in format: collected, time, fitness
for c, t, f in zip(collected_resources, completed_time, fitness):
    print(f"{c}, {t}, {f:.2f}")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(range(len(fitness)), fitness, marker='o')
plt.axvline(x=5, color='red', linestyle='--')  # Vertical red line at index 5
plt.title("Fitness Function")
plt.xlabel("Solution Index")
plt.ylabel("Fitness")
# plt.grid(True)
plt.show()
