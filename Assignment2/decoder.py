import argparse
import numpy as np

parser = argparse.ArgumentParser(description="DECODER")
parser.add_argument("--opponent", type=str, help="Path to opponent policy file", required=True)
parser.add_argument("--value-policy", dest="value_policy", type=str, help="Value and Policy file (i.e. output of planner.py)", required=True)
args = parser.parse_args()

opponent_policy = dict()

with open(args.opponent, 'r') as fp:
    for line in fp:
        d = line.split()
        if d[0] == "state":
            continue
        opponent_policy[d[0]] = [float(d[i]) for i in range(1,5)]

numStates = len(opponent_policy.keys())

value_function = np.zeros(numStates)
policy = np.zeros(numStates, dtype=int)
index = 0

with open(args.value_policy, 'r') as fp:
    for line in fp:
        d = line.split()
        policy[index] = int(d[1]) 
        value_function[index] = float(d[0])
        index += 1
        if index == 8192:
            break

states = []
for state in opponent_policy.keys():
    states.append(state)

for i in range(numStates):
    print(states[i], policy[i], "{:.6f}".format(value_function[i]))