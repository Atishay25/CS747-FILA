"""
NOTE: You are only allowed to edit this file between the lines that say:
    # START EDITING HERE
    # END EDITING HERE

This file contains the base Algorithm class that all algorithms should inherit
from. Here are the method details:
    - __init__(self, num_arms, horizon): This method is called when the class
        is instantiated. Here, you can add any other member variables that you
        need in your algorithm.
    
    - give_pull(self): This method is called when the algorithm needs to
        select an arm to pull. The method should return the index of the arm
        that it wants to pull (0-indexed).
    
    - get_reward(self, arm_index, reward): This method is called just after the 
        give_pull method. The method should update the algorithm's internal
        state based on the arm that was pulled and the reward that was received.
        (The value of arm_index is the same as the one returned by give_pull.)

We have implemented the epsilon-greedy algorithm for you. You can use it as a
reference for implementing your own algorithms.
"""

import numpy as np
import math
# Hint: math.log is much faster than np.log for scalars

class Algorithm:
    def __init__(self, num_arms, horizon):
        self.num_arms = num_arms
        self.horizon = horizon
    
    def give_pull(self):
        raise NotImplementedError
    
    def get_reward(self, arm_index, reward):
        raise NotImplementedError

# Example implementation of Epsilon Greedy algorithm
class Eps_Greedy(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # Extra member variables to keep track of the state
        self.eps = 0.1
        self.counts = np.zeros(num_arms)
        self.values = np.zeros(num_arms)
    
    def give_pull(self):
        if np.random.random() < self.eps:
            return np.random.randint(self.num_arms)
        else:
            return np.argmax(self.values)
    
    def get_reward(self, arm_index, reward):
        self.counts[arm_index] += 1
        n = self.counts[arm_index]
        value = self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value

# START EDITING HERE
# You can use this space to define any helper functions that you need
# KL function used for KL-UCB
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

class UCB(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # START EDITING HERE
        self.ucb = np.zeros(num_arms)       # Array for UCB values for each arm 
        self.values = np.zeros(num_arms)    # Empirical mean of rewards for each arm
        self.count = np.zeros(num_arms)     # Number of times each arm has been sampled
        self.time = 0                       # Variable to keep track of time
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        return np.argmax(self.ucb)
        # END EDITING HERE  
        
    
    def get_reward(self, arm_index, reward):
        # START EDITING HERE
        self.time += 1
        self.count[arm_index] += 1
        n = self.count[arm_index]
        value = self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value
        for arm in range(self.num_arms):
            self.ucb[arm] = self.values[arm] + math.sqrt((2*math.log(self.time))/(self.count[arm]+1e-6))
        # END EDITING HERE


class KL_UCB(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # You can add any other variables you need here
        # START EDITING HERE
        self.klucb = np.zeros(num_arms)         # Array for KL-UCB values for each arm 
        self.values = np.zeros(num_arms)        # Empirical mean of rewards for each arm
        self.count = np.zeros(num_arms)         # Number of times each arm has been sampled
        self.time = 0                           # Variable to keep track of time
        self.c = 0                              # KL_UCB parameter c, using c = 0
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        self.time +=  1
        # wanted = math.log(self.time + 1e-6) + self.c * math.log(math.log(self.time + 1e-6))
        wanted = math.log(self.time)        # as I am using c = 0, wanted term is this itself
        for arm in range(self.num_arms):
            q_vals = np.arange(self.values[arm],1,0.01)     # taking precision of 0.01 in binary search
            l = 0
            r = len(q_vals) - 1
            if(r == -1):
                self.klucb[arm] = 1
                continue
            mid = (l+r)//2
            q = 0
            while l <= r:       # USING BINARY SEARCH
                mid = (l+r)//2
                if (self.count[arm] * KL(self.values[arm],q_vals[mid]) <= wanted):
                    q = q_vals[mid]
                    l = mid + 1
                else:
                    r = mid - 1
            self.klucb[arm] = q 
            # l = self.values[arm]          # USING BISECTION METHOD
            # r = 1
            # while abs(l-r) > 1e-2:
            #     mid = (l+r)/2
            #     if (self.count[arm] * KL(self.values[arm],mid) <= wanted):
            #         l = mid
            #     else:
            #         r = mid
            # self.klucb[arm] = l
        return np.argmax(self.klucb)
        # END EDITING HERE
    
    def get_reward(self, arm_index, reward):
        # START EDITING HERE
        self.count[arm_index] += 1
        n = self.count[arm_index]
        value = self.values[arm_index]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm_index] = new_value
        # END EDITING HERE

class Thompson_Sampling(Algorithm):
    def __init__(self, num_arms, horizon):
        super().__init__(num_arms, horizon)
        # You can add any other variables you need here
        # START EDITING HERE
        self.values = np.zeros(num_arms)        # Array of sample drawn for each arm from beta distribution
        self.success = np.zeros(num_arms)       # Number of successes for each arm 
        self.fail = np.zeros(num_arms)          # Number of failures for each arm
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        for arm in range(self.num_arms):
            self.values[arm] = np.random.beta(self.success[arm] + 1, self.fail[arm] + 1)
        return np.argmax(self.values)
        # END EDITING HERE
    
    def get_reward(self, arm_index, reward):
        # START EDITING HERE
        if reward == 0:
            self.fail[arm_index] += 1
        else:
            self.success[arm_index] += 1
        # END EDITING HERE
