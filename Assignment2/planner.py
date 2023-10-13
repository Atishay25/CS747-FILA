import argparse
import numpy as np
import pulp as pl

def value_iteration(numStates, numActions, T, R, gamma):
    V = np.zeros(numStates, dtype=float)
    theta = 1e-10
    while 1:
        d = 0
        for s in range(numStates):
            v = V[s]
            V[s] = np.max(np.sum(T[s,:,:]*(R[s,:,:]+gamma*V), axis=1),axis=0)
            d = max(d, abs(v-V[s]))
        if d < theta:
            break
    policy = np.argmax(np.sum(T*(R + gamma * V), axis=2), axis=1)
    return V, policy

'''
This algorithm hpi has a subtle bug, in that it may never terminate if the policy continually switches between two or more policies that are equally good. The bug
can be fixed by adding additional flags, but it makes the pseudocode so ugly
that it is not worth it. :-)
'''
def hpi(numStates, T, R, gamma):
    pi = np.zeros(numStates, dtype=int)
    value = np.zeros(numStates)
    while True:
        while True:
            delta = 0
            for s in range(numStates):
                v = value[s]
                value[s] = np.sum(T[s, pi[s],:] * (R[s, pi[s],:] + gamma * value), axis=0)
                delta = max(delta, abs(v - value[s]))
            if delta < 1e-10:
                break
        policy_stable = True
        for s in range(numStates):
            a = pi[s]
            pi[s] = np.argmax(np.sum(T[s,:,:]*(R[s,:,:] + gamma * value), axis=1), axis=0)
            if a != pi[s]:
                policy_stable = False
        if policy_stable:
            break
    return value, pi

def lp(numStates, numActions, T, R, gamma):
    prob = pl.LpProblem("MDP", pl.LpMaximize)
    v = pl.LpVariable.dicts("V",[i for i in range(numStates)])
    prob += pl.lpSum([-1*v[i] for i in range(numStates)])
    for i in range(numStates):
        for j in range(numActions):
            prob += v[i] >= pl.lpSum([T[i][j][k] * (R[i][j][k] + gamma*v[k]) for k in range(numStates)]) 
    prob.solve(pl.PULP_CBC_CMD(msg=0))
    v_soln = np.array([float(pl.value(v[i])) for i in range(numStates)])
    pi_soln = np.argmax(np.sum(T*(R + gamma * v_soln), axis=2), axis=1)
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
            value_function[s] = np.sum(T[s, policy[s],:] * (R[s, policy[s],:] + gamma * value_function), axis=0)
            delta = max(delta, abs(v - value_function[s]))
        if delta < 1e-10:
            break
    return value_function, policy

parser = argparse.ArgumentParser(description='MDP Planner')
parser.add_argument("--mdp", type=str, help="Path to the input MDP file", required=True)
parser.add_argument("--algorithm", choices=['vi', 'hpi', 'lp'], help="Algorithm: vi, hpi, or lp", default='hpi',required=False)
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
            T = np.zeros((numStates, numActions, numStates))
            R = np.zeros((numStates, numActions, numStates))
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
    V, pi = hpi(numStates, T, R, gamma)
elif algo == 'lp':
    V, pi = lp(numStates, numActions, T, R, gamma)
else:
    V, pi = value_iteration(numStates, numActions, T, R, gamma)
for j in range(numStates):
    print("{:.6f}".format(V[j]), pi[j])
