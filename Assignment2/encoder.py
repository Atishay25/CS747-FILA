import argparse
import numpy as np

def y_corr(pos):
    return (pos-1)//4

def x_corr(pos):
    return (pos-1)%4

# Function to get index of a given state
def state_to_index(x):
    b1, b2, r, possession = int(x[:2]), int(x[2:4]), int(x[4:6]), int(x[6])
    return (b1-1)*512 + (b2-1)*32 + (r-1)*2 + (possession-1)

parser = argparse.ArgumentParser(description="MDP ENCODER")
parser.add_argument("--opponent", type=str, help="Path to opponent policy file", required=True)
parser.add_argument("--p", type=float, help="Paramter p", required=True)
parser.add_argument("--q", type=float, help="Paramter q", required=True)
args = parser.parse_args()

p = args.p
q = args.q
numStates = 2*(16**3) + 2
numActions = 10
endStates = [numStates-2, numStates-1]
mdptype = "episodic"
gamma = 1

opponent_policy = dict()

with open(args.opponent, 'r') as fp:
    for line in fp:
        d = line.split()
        if d[0] == "state":
            continue
        opponent_policy[d[0]] = [float(d[i]) for i in range(1,5)]
        
states = []
index = 0
for state in opponent_policy.keys():
    states.append(state)
    index += 1

movement = {0:-1, 1:1, 2:-4, 3:4}

print("numStates", numStates)
print("numActions", numActions)
print("end", end=" ")
for i in endStates:
    print(i, end=" ")
print("\n", end="")

for s in range(numStates-2):  
    for action in range(10):
        next_state = ""
        t1 = 0
        t2 = 0
        if action in range(4):
            b1_pos = int(states[s][:2])
            if (action == 0 and b1_pos % 4 == 1) or (action == 1 and b1_pos % 4 == 0) or (action == 2 and b1_pos <= 4) or (action == 3 and b1_pos >= 13):
                print("transition", s, action, endStates[1], 0, 1)
                continue
            b1_pos += movement[action]
            if b1_pos <= 16 and b1_pos >= 1:
                if b1_pos < 10:
                    next_state = "0" + str(b1_pos) + states[s][2:] 
                else:
                    next_state = str(b1_pos) + states[s][2:]
        elif action in range(4,8):
            b2_pos = int(states[s][2:4])
            if (action == 4 and b2_pos % 4 == 1) or (action == 5 and b2_pos % 4 == 0) or (action == 6 and b2_pos <= 4) or (action == 7 and b2_pos >= 13):
                print("transition", s, action, endStates[1], 0, 1)
                continue
            b2_pos += movement[action-4]
            if b2_pos <= 16 and b2_pos >= 1:
                if b2_pos < 10:
                    next_state =  states[s][:2] + "0" + str(b2_pos) + states[s][4:] 
                else:
                    next_state = states[s][:2] + str(b2_pos) + states[s][4:]
        elif action == 8:
            if states[s][6] == "1":
                next_state = states[s][:6] + "2"
            else:
                next_state = states[s][:6] + "1"
        elif action == 9:
            next_state = states[s]
        transition = dict()
        transition[endStates[0]] = 0
        transition[endStates[1]] = 0
        for r_action in range(4):
            r_pos = int(states[s][4:6])
            next_state1 = ""
            if (r_action == 0 and r_pos % 4 == 1) or (r_action == 1 and r_pos % 4 == 0) or (r_action == 2 and r_pos <= 4) or (r_action == 3 and r_pos >= 13):
                continue
            r_pos += movement[r_action]
            if r_pos <= 16 and r_pos >= 1:
                if r_pos < 10:
                    next_state1 = next_state[:4] + "0" + str(r_pos) + next_state[6]
                else:
                    next_state1 = next_state[:4] + str(r_pos) + next_state[6]
            if state_to_index(next_state1) not in transition.keys():
                transition[state_to_index(next_state1)] = 0
            if action in range(4): # b1 moves 
                if states[s][6] == "1":
                    t1 = 1 - 2*p
                    t2 = 2*p
                    if (next_state1[:2] == next_state1[4:6]) or (states[s][:2] == next_state1[4:6] and states[s][4:6] == next_state1[:2]):
                        t1 = t1*0.5
                        t2 = 1 - t1
                else:
                    t1 = 1-p
                    t2 = p
            elif action in range(4,8): # b2 moves 
                if states[s][6] == "2":
                    t1 = (1-2*p)
                    t2 = 2*p
                    if (next_state1[2:4] == next_state1[4:6]) or (states[s][2:4] == next_state1[4:6] and states[s][4:6] == next_state1[2:4]):
                        t1 = t1*0.5
                        t2 = 1 - t1
                else:
                    t1 = (1-p)
                    t2 = p
            elif action == 8:   # pass
                b1 = int(next_state1[:2])
                b2 = int(next_state1[2:4])
                r_next = int(next_state1[4:6])
                x1, x2 = x_corr(b1), x_corr(b2)
                y1, y2 = y_corr(b1), y_corr(b2)
                r_x, r_y = x_corr(r_next), y_corr(r_next)
                t1 = q - 0.1*max(abs(x1-x2), abs(y1-y2))
                if x1 == r_x and r_x == x2 and ((r_y <= y2 and r_y >= y1) or (r_y >= y2 and r_y <= y1)):
                    t1 = t1*0.5
                elif y1 == r_y and y2 == r_y and ((r_x <= x2 and r_x >= x1) or (r_x >= x2 and r_x <= x1)):
                    t1 = t1*0.5
                elif (x1+y1 == r_x+r_y) and (x2+y2 == r_x+r_y) and ((r_x <= x2 and r_x >= x1) or (r_x >= x2 and r_x <= x1)) :
                    t1 = t1*0.5
                elif (x1-y1 == r_x-r_y) and (x2-y2 == r_x-r_y) and ((r_x <= x2 and r_x >= x1) or (r_x >= x2 and r_x <= x1)):
                    t1 = t1*0.5
                t2 = 1 - t1
            elif action == 9:
                shooting_x = 0
                if states[s][6] == "1":
                    shooting_x = x_corr(int(states[s][:2]))
                else:
                    shooting_x = x_corr(int(states[s][2:4]))
                r_next = int(next_state1[4:6])
                t1 = q - 0.2*(3-shooting_x)
                if r_next == 8 or r_next == 12:
                    t1 = t1 * 0.5
                t2 = 1-t1
            t1 = t1 * opponent_policy[states[s]][r_action]
            t2 = t2 * opponent_policy[states[s]][r_action]
            if action != 9:
                transition[state_to_index(next_state1)] += t1
            else:
                transition[endStates[0]] += t1
            transition[endStates[1]] += t2
        for t in transition.keys():
            if transition[t] != 0:
                if t == endStates[0]:
                    print("transition", s, action, t, 1, transition[t])
                else:
                    print("transition", s, action, t, 0, transition[t])

print("mdptype", mdptype)
print("discount",  gamma)
