"""
You need to write code to plot the graphs as required in task2 of the problem statement:
    - You can edit any code in this file but be careful when modifying the simulation specific code. 
    - The simulation framework as well as the BernoulliBandit implementation for this task have been separated from the rest of the assignment code and is contained solely in this file. This will be useful in case you would like to collect more information from runs rather than just regret.
"""

import numpy as np
from multiprocessing import Pool
from task1 import Eps_Greedy, UCB, KL_UCB
import matplotlib.pyplot as plt
# START EDITING HERE
# You can use this space to define any helper functions that you need.
import math
def KL(x,y):
    y1 = y - 1e-10
    y2 = y + 1e-10
    if x == 0:
        return (1-x)*math.log((1-x)/(1-y1))
    elif x == 1:
        return x*math.log(x/y2)
    else:       
        return x*math.log(x/y2) + (1-x)*math.log((1-x)/(1-y1))
# END EDITING HERE

class BernoulliArmTask2:
  def __init__(self, p):
    self.p = p

  def pull(self, num_pulls=None):
    return np.random.binomial(1, self.p, num_pulls)

class BernoulliBanditTask2:
  def __init__(self, probs=[0.3, 0.5, 0.7],):
    self.__arms = [BernoulliArmTask2(p) for p in probs]
    self.__max_p = max(probs)
    self.__regret = 0

  def pull(self, index):
    reward = self.__arms[index].pull()
    self.__regret += self.__max_p - reward
    return reward

  def regret(self):
    return self.__regret
  
  def num_arms(self):
    return len(self.__arms)


def single_sim_task2(seed=0, ALGO=Eps_Greedy, PROBS=[0.3, 0.5, 0.7], HORIZON=1000):
  np.random.seed(seed)
  np.random.shuffle(PROBS)
  bandit = BernoulliBanditTask2(probs=PROBS)
  algo_inst = ALGO(num_arms=len(PROBS), horizon=HORIZON)
  for t in range(HORIZON):
    arm_to_be_pulled = algo_inst.give_pull()
    reward = bandit.pull(arm_to_be_pulled)
    algo_inst.get_reward(arm_index=arm_to_be_pulled, reward=reward)
  return bandit.regret()

def simulate_task2(algorithm, probs, horizon, num_sims=50):
  """simulates algorithm of class Algorithm
  for BernoulliBandit bandit, with horizon=horizon
  """
  
  def multiple_sims(num_sims=50):
    with Pool(10) as pool:
      sim_out = pool.starmap(single_sim_task2,
        [(i, algorithm, probs, horizon) for i in range(num_sims)])
    return sim_out 

  sim_out = multiple_sims(num_sims)
  regrets = np.mean(sim_out)

  return regrets

def task2(algorithm, horizon, p1s, p2s, num_sims=50):
    """generates the data for task2
    """
    probs = [[p1s[i], p2s[i]] for i in range(len(p1s))]

    regrets = []
    for prob in probs:
        regrets.append(simulate_task2(algorithm, prob, horizon, num_sims))

    return regrets

if __name__ == '__main__':
  # INSERT YOUR CODE FOR PLOTTING HERE
  # TASK2 (A)
  p1 = 0.9
  task2p2s = np.arange(0,p1+0.01,0.05)
  task2p1s = p1 * np.ones(len(task2p2s))

  regrets2a = task2(UCB, 30000, task2p1s, task2p2s, 50)

  fig2a, ax = plt.subplots(figsize=(10, 6))
  ax.plot(task2p2s, regrets2a, marker='o', linestyle='-', color='b', label="UCB")
  ax.set_title("Task2A: Variation of Regret with p2", fontsize=14)
  ax.set_xlabel("p2 (Mean of the second arm)", fontsize=12)
  ax.set_ylabel("Regret", fontsize=12)
  ax.grid(True, linestyle='--', alpha=0.6)
  ax.tick_params(axis='both', which='major', labelsize=10)
  plt.legend()
  plt.savefig("task2a.png")
  plt.show()

  # TASK 2 (B)
  task2p1sb = 0.1 + task2p2s
  regrets_ucb = task2(UCB, 30000, task2p1sb, task2p2s, 50)
  regrets_klucb = task2(KL_UCB, 30000, task2p1sb, task2p2s, 50)

  fig2b1, axb1 = plt.subplots(figsize=(10, 6))
  axb1.plot(task2p2s, regrets_ucb, marker='o', linestyle='-', color='b', label="UCB")
  axb1.set_title("Task2B: Variation of Regret with p2 for UCB", fontsize=14)
  axb1.set_xlabel("p2 (Mean of the second arm)", fontsize=12)
  axb1.set_ylabel("Regret", fontsize=12)
  axb1.grid(True, linestyle='--', alpha=0.6)
  axb1.tick_params(axis='both', which='major', labelsize=10)
  plt.legend()
  plt.savefig("task2b_ucb.png")
  plt.show()

  fig2b2, axb2 = plt.subplots(figsize=(10, 6))
  axb2.plot(task2p2s, regrets_klucb,label='KL-UCB', marker='o', linestyle='-', color='b')
  axb2.set_title("Task2B: Variation of Regret with p2 for KL-UCB", fontsize=14)
  axb2.set_xlabel("p2 (Mean of the second arm)", fontsize=12)
  axb2.set_ylabel("Regret", fontsize=12)
  axb2.grid(True, linestyle='--', alpha=0.6)
  axb2.tick_params(axis='both', which='major', labelsize=10)
  plt.legend()
  plt.savefig("task2b_klucb.png")
  plt.show()
  
  # Additional plot for part (b) KLUCB plot, with Lower bounds also plotted
  # lower_bound = np.zeros(len(task2p1s))
  # lower_bound = [0.1/KL(task2p1sb[i], task2p2s[i]) for i in range(len(task2p1s))]
  # fig2b3, axb3 = plt.subplots(figsize=(10, 6))
  # axb3.plot(task2p2s, regrets_klucb,label='Regret', marker='o', linestyle='-', color='b')
  # axb3.plot(task2p2s, lower_bound,label='Lower Bound', marker='o', linestyle='-', color='r')
  # axb3.set_title("Task2B: Variation of Regret with p2 for KL-UCB", fontsize=14)
  # axb3.set_xlabel("p2 (Mean of the second arm)", fontsize=12)
  # axb3.set_ylabel("Regret", fontsize=12)
  # axb3.grid(True, linestyle='--', alpha=0.6)
  # axb3.tick_params(axis='both', which='major', labelsize=10)
  # plt.legend()
  # plt.savefig("task2b_klucb_with_lowerbound.png")
  # plt.show()

  # Uncomment these lines for printing the values
  #print("TASK 2A :")
  #for i in range(len(task2p2s)):
  #  print(f"P1: {task2p1s[i]},\t P2: {round(task2p2s[i],2)},\t REGRET: {regrets2a[i]}")
  #print("TASK 2B :")
  #for i in range(len(task2p2s)):
  #  print(f"P1: {task2p1sb[i]},\t P2: {round(task2p2s[i],2)},\t REGRET_UCB: {regrets_ucb[i]}, \t REGRET_KLUCB: {regrets_klucb[i]}")


