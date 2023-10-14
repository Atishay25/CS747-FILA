import matplotlib.pyplot as plt

# Sample data (you'll need to compute the actual probabilities)
p_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
q_values = [0.6, 0.7, 0.8, 0.9, 1]
winning_probabilities_graph1 = [0.7, 0.75, 0.78, 0.82, 0.85, 0.88]  # Replace with actual probabilities
winning_probabilities_graph2 = [0.65, 0.7, 0.75, 0.8, 0.85]  # Replace with actual probabilities
start_state = "0509081"

# Graph 1: Varying p
plt.figure(1)
plt.plot(p_values, winning_probabilities_graph1, marker='o', linestyle='-')
plt.title("Probability of Winning vs. p (q = 0.7)")
plt.xlabel("p")
plt.ylabel("Probability of Winning")
plt.grid(True)

# Graph 2: Varying q
plt.figure(2)
plt.plot(q_values, winning_probabilities_graph2, marker='o', linestyle='-')
plt.title("Probability of Winning vs. q (p = 0.3)")
plt.xlabel("q")
plt.ylabel("Probability of Winning")
plt.grid(True)

plt.show()
