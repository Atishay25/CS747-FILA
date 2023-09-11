"""
NOTE: You are only allowed to edit this file between the lines that say:
    # START EDITING HERE
    # END EDITING HERE

This file contains the FaultyBanditsAlgo class. Here are the method details:
    - __init__(self, num_arms, horizon, fault): This method is called when the class
        is instantiated. Here, you can add any other member variables that you
        need in your algorithm.
    
    - give_pull(self): This method is called when the algorithm needs to
        select an arm to pull. The method should return the index of the arm
        that it wants to pull (0-indexed).
    
    - get_reward(self, arm_index, reward): This method is called just after the 
        give_pull method. The method should update the algorithm's internal
        state based on the arm that was pulled and the reward that was received.
        (The value of arm_index is the same as the one returned by give_pull.)
"""

import numpy as np

# START EDITING HERE
# You can use this space to define any helper functions that you need
# END EDITING HERE

class FaultyBanditsAlgo:
    def __init__(self, num_arms, horizon, fault):
        # You can add any other variables you need here
        self.num_arms = num_arms
        self.horizon = horizon
        self.fault = fault # probability that the bandit returns a faulty pull
        # START EDITING HERE
        self.values = np.zeros(num_arms)
        self.success = np.zeros(num_arms)
        self.fail = np.zeros(num_arms)
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        # using thompson sampling with samples taken in range [p/2,1-p/2]
        for arm in range(self.num_arms):
            self.values[arm] = np.random.beta(self.success[arm] + 1, self.fail[arm] + 1)
            #while 1:
            #    if (self.values[arm] <= (1-(self.fault/2)) and self.values[arm] >= (self.fault)/2):
            #        break
            #    self.values[arm] = np.random.beta(self.success[arm] + 1, self.fail[arm] + 1)
        return np.argmax(self.values)
        # END EDITING HERE
    
    def get_reward(self, arm_index, reward):
        # START EDITING HERE
        # NORMAL THOMPSON
        if reward == 0:
            self.fail[arm_index] += 9/8
            self.success[arm_index] -= 1/8
        else:
            self.success[arm_index] += 9/8
            self.fail[arm_index] -= 1/8
        self.success[arm_index] = max(0,self.success[arm_index])
        self.fail[arm_index] = max(0,self.fail[arm_index])
        #END EDITING HERE

