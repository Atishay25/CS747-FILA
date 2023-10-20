import matplotlib.pyplot as plt
import subprocess,os

# Used same run function as given in autograder.py
def run(opponent, p, q):
    cmd_encoder = "python","encoder.py","--opponent", opponent, "--p", str(p), "--q", str(q)
    #print("\n","Generating the MDP encoding using encoder.py")
    f = open('verify_attt_mdp','w')
    subprocess.call(cmd_encoder,stdout=f)
    f.close()

    cmd_planner = "python","planner.py","--mdp","verify_attt_mdp"
    #print("\n","Generating the value policy file using planner.py using default algorithm")
    f = open('verify_attt_planner','w')
    subprocess.call(cmd_planner,stdout=f)
    f.close()

    cmd_decoder = "python","decoder.py","--value-policy","verify_attt_planner","--opponent", opponent 
    #print("\n","Generating the decoded policy file using decoder.py")
    cmd_output = subprocess.check_output(cmd_decoder,universal_newlines=True)

    os.remove('verify_attt_mdp')
    os.remove('verify_attt_planner')
    return cmd_output

# Function to get index of a given state
def state_to_index(x):
    b1, b2, r, possession = int(x[:2]), int(x[2:4]), int(x[4:6]), int(x[6])
    return (b1-1)*512 + (b2-1)*32 + (r-1)*2 + (possession-1)

p1 = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
q1 = 0.7
p2 = 0.3
q2 = [0.6, 0.7, 0.8, 0.9, 1]

prob1 = []  
prob2 = []  
start_state_ = "0509081"
print("Start State:", start_state_)
start_state = state_to_index(start_state_)
in_file = "data/football/test-1.txt"
w_prob = 0
action = 0

for p in p1:
    print("Running for ", in_file, ' with parameters', p, q1)
    output = run(in_file, p, q1)
    output = output.split('\n')
    output.remove('')
    w_prob = float(output[start_state].split(' ')[2])
    prob1.append(w_prob)
    action = int(output[start_state].split(' ')[1])
    print("Winning Probability:", w_prob, " Optimal Action:", action, "\n")

for q in q2:
    print("Running for ", in_file, ' with parameters', p2, q)
    output = run(in_file, p2, q)
    output = output.split('\n')
    output.remove('')
    w_prob = float(output[start_state].split(' ')[2])
    prob2.append(w_prob)
    action = int(output[start_state].split(' ')[1])
    print("Winning Probability:", w_prob, " Optimal Action:", action, "\n")

print("Winning Probabilities of Graph1 = ",prob1)
print("Winning Probabilities of Graph2 = ",prob2)

# Graph 1
plt.figure(1)
plt.plot(p1, prob1, marker='o', linestyle='-',color='red', label="Start State = " + start_state_)
plt.title("Probability of Winning vs. p (at q = " + str(q1) + ")")
plt.xlabel("p")
plt.ylabel("Probability of Winning")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tick_params(axis='both', which='major', labelsize=10)
plt.legend()
plt.savefig("graph1.png")

# Graph 2
plt.figure(2)
plt.plot(q2, prob2, marker='o', linestyle='-', label="Start State = " + start_state_)
plt.title("Probability of Winning vs. q (at p = " + str(p2) + ")")
plt.xlabel("q")
plt.ylabel("Probability of Winning")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tick_params(axis='both', which='major', labelsize=10)
plt.legend()
plt.savefig("graph2.png")

plt.show()
