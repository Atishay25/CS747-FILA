import numpy as np

def to_rep(x):
    if x == 8192 or x == 8193:
        return x
    ball = x//4096 + 1
    x = x%4096
    r = x//256 + 1
    x = x % 256
    b2 = x//16 + 1
    x = x%16
    b1 = x+1
    return (b1-1)*512 + (b2-1)*32 + (r-1)*2 + (ball-1)

def to_num(x):
    b1,b2,r,ball = int(x[:2]), int(x[2:4]), int(x[4:6]), int(x[6])
    return (ball-1)*4096 + (r-1)*256 + (b2-1)*16 + (b1-1)

t1 = None
t2 = None

with open('football_mdp.txt', 'r') as fp:
    for line in fp:
        d = line.split()
        if d[0] == "numStates":
            numStates = int(d[1])
        elif d[0] == "numActions":
            numActions = int(d[1])
            t1 = np.zeros((numStates, numActions, numStates))
        elif d[0] == "end":
            end = list(map(int, d[1:]))
        elif d[0] == "mdptype":
            mdptype = d[1]
        elif d[0] == "discount":
            gamma = float(d[1])
        else:
            t1[int(d[1])][int(d[2])][int(d[3])] = float(d[5])

with open('sachi.txt', 'r') as fp:
    for line in fp:
        d = line.split()
        if d[0] == "numStates":
            numStates = int(d[1])
        elif d[0] == "numActions":
            numActions = int(d[1])
            t2 = np.zeros((numStates, numActions, numStates))
        elif d[0] == "end":
            end = list(map(int, d[1:]))
        elif d[0] == "mdptype":
            mdptype = d[1]
        elif d[0] == "discount":
            gamma = float(d[1])
        else:
            t2[to_rep(int(d[1]))][int(d[2])][to_rep(int(d[3]))] = float(d[5])

for i in range(numStates):
    for j in range(numActions):
        for k in range(numStates):
            if t1[i][j][k] != t2[i][j][k]:
                print(i,j,k,t1[i][j][k],t2[i][j][k])
                exit()
print("theek")