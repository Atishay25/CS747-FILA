import argparse
import numpy as np
import pulp as pl

# Value Iteration
def value_iteration(numStates, numActions, T, R, gamma):
    value_function = np.zeros(numStates, dtype=float)
    while True:
        d = 0
        for s in range(numStates):
            v = value_function[s]
            # V[s] = np.max(np.sum(T[s,:,:]*(R[s,:,:]+gamma*V), axis=1),axis=0)
            arr = np.zeros(numActions)
            for j in range(numActions):
                new_sum = 0
                for k in T[s][j].keys():
                    new_sum += T[s][j][k] * (R[s][j][k] + gamma * value_function[k])
                arr[j] = new_sum
            value_function[s] = np.max(arr)
            d = max(d, abs(v-value_function[s]))
        if d < 1e-12:
            break
    # policy = np.argmax(np.sum(T*(R + gamma * V), axis=2), axis=1)
    policy = np.zeros(numStates, dtype=int)
    for s in range(numStates):
        arr = np.zeros(numActions)
        for j in range(numActions):
            for k in T[s][j].keys():
                arr[j] += (T[s][j][k] * (R[s][j][k] + gamma * value_function[k]))
        policy[s] = np.argmax(arr)
    return value_function, policy

# Howards Policy Iteration
def hpi(numStates, numActions, T, R, gamma):
    pi = np.zeros(numStates, dtype=int)
    value = np.zeros(numStates)
    while True:
        while True:
            delta = 0
            for s in range(numStates):
                v = value[s]
                # value[s] = np.sum(T[s, pi[s],:] * (R[s, pi[s],:] + gamma * value), axis=0)
                new_sum = 0
                for k in T[s][pi[s]].keys():
                    new_sum += T[s][pi[s]][k] * (R[s][pi[s]][k] + gamma * value[k])
                value[s] = new_sum
                delta = max(delta, abs(v - value[s]))
            if delta < 1e-12:
                break
        policy_stable = True
        for s in range(numStates):
            a = pi[s]
            # pi[s] = np.argmax(np.sum(T[s,:,:]*(R[s,:,:] + gamma * value), axis=1), a
            arr = np.zeros(numActions)
            for j in range(numActions):
                for k in T[s][j].keys():
                    arr[j] += (T[s][j][k] * (R[s][j][k] + gamma * value[k]))
            pi[s] = np.argmax(arr)
            if a != pi[s]:
                policy_stable = False
        if policy_stable:
            break
    return value, pi

# Linear Programming
def lp(numStates, numActions, T, R, gamma):
    prob = pl.LpProblem("MDP", pl.LpMaximize)
    v = pl.LpVariable.dicts("V",[i for i in range(numStates)])
    prob += pl.lpSum([-1*v[i] for i in range(numStates)])
    for i in range(numStates):
        for j in range(numActions):
            prob += v[i] >= pl.lpSum([T[i][j][k] * (R[i][j][k] + gamma*v[k]) for k in T[i][j].keys()]) 
    prob.solve(pl.PULP_CBC_CMD(msg=0))
    v_soln = np.array([float(pl.value(v[i])) for i in range(numStates)])
    # pi_soln = np.argmax(np.sum(T*(R + gamma * v_soln), axis=2), axis=1)
    pi_soln = np.zeros(numStates, dtype=int)
    for s in range(numStates):
        arr = np.zeros(numActions)
        for j in range(numActions):
            for k in T[s][j].keys():
                arr[j] += (T[s][j][k] * (R[s][j][k] + gamma * v_soln[k]))
        pi_soln[s] = np.argmax(arr)
    return v_soln, pi_soln

def policy_evaluation(numStates, numActions, T, R, gamma, policy_file):
    policy = np.zeros(numStates, dtype=int)
    index = 0
    with open(policy_file, 'r') as fp:
        for line in fp:
            d = line.split()
            policy[index] = d[0]
            index += 1
    value_function = np.zeros(numStates, dtype=float)
    while True:
        delta = 0
        for s in range(numStates):
            v = value_function[s]
            # value_function[s] = np.sum(T[s, policy[s],:] * (R[s, policy[s],:] + gamma * value_function), axis=0)
            new_sum = 0
            for k in T[s][policy[s]].keys():
                new_sum += T[s][policy[s]][k] * (R[s][policy[s]][k] + gamma * value_function[k])
            value_function[s] = new_sum
            delta = max(delta, abs(v - value_function[s]))
        if delta < 1e-12:
            break
    return value_function, policy

parser = argparse.ArgumentParser(description='MDP Planner')
parser.add_argument("--mdp", type=str, help="Path to the input MDP file", required=True)
parser.add_argument("--algorithm", choices=['vi', 'hpi', 'lp'], help="Algorithm: vi, hpi, or lp", default='vi',required=False)
parser.add_argument("--policy", type=str, help="Path to the policy", required=False)

args = parser.parse_args()
mdp_file = args.mdp
algo = args.algorithm
end = []
numStates = int()
numActions = int()
mdptype = str()
gamma = float()
T = None
R = None

with open(mdp_file, 'r') as fp:
    for line in fp:
        d = line.split()
        if d[0] == "numStates":
            numStates = int(d[1])
        elif d[0] == "numActions":
            numActions = int(d[1])
            T = [[dict() for k in range(numActions)] for i in range(numStates)]
            R = [[dict() for k in range(numActions)] for i in range(numStates)]
        elif d[0] == "end":
            end = list(map(int, d[1:]))
        elif d[0] == "mdptype":
            mdptype = d[1]
        elif d[0] == "discount":
            gamma = float(d[1])
        else:
            T[int(d[1])][int(d[2])][int(d[3])] = float(d[5])
            R[int(d[1])][int(d[2])][int(d[3])] = float(d[4])

V, pi = np.zeros(numStates), np.zeros(numStates, dtype=int)

if args.policy:
    V, pi = policy_evaluation(numStates, numActions, T, R, gamma, args.policy)
elif algo == 'vi':
    V, pi = value_iteration(numStates, numActions, T, R, gamma)
elif algo == 'hpi':
    V, pi = hpi(numStates, numActions, T, R, gamma)
elif algo == 'lp':
    V, pi = lp(numStates, numActions, T, R, gamma)
else:
    V, pi = value_iteration(numStates, numActions, T, R, gamma)
    
for j in range(numStates):
    print("{:.6f}".format(V[j]), pi[j])
