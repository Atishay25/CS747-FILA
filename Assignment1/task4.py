"""
NOTE: You are only allowed to edit this file between the lines that say:
    # START EDITING HERE
    # END EDITING HERE

This file contains the MultiBanditsAlgo class. Here are the method details:
    - __init__(self, num_arms, horizon): This method is called when the class
        is instantiated. Here, you can add any other member variables that you
        need in your algorithm.
    
    - give_pull(self): This method is called when the algorithm needs to
        select an arm to pull. The method should return the index of the arm
        that it wants to pull (0-indexed).
    
    - get_reward(self, arm_index, set_pulled, reward): This method is called 
        just after the give_pull method. The method should update the 
        algorithm's internal state based on the arm that was pulled and the 
        reward that was received.
        (The value of arm_index is the same as the one returned by give_pull 
        but set_pulled is the set that is randomly chosen when the pull is 
        requested from the bandit instance.)
"""

import numpy as np

# START EDITING HERE
# You can use this space to define any helper functions that you need
# END EDITING HERE


class MultiBanditsAlgo:
    def __init__(self, num_arms, horizon):
        # You can add any other variables you need here
        self.num_arms = num_arms
        self.horizon = horizon
        # START EDITING HERE
        self.values = np.zeros((2,num_arms))
        self.success = np.zeros((2,num_arms))
        self.fail = np.zeros((2,num_arms))
        # END EDITING HERE
    
    def give_pull(self):
        # START EDITING HERE
        # THOMPSON SAMPLING WITH AVERAGING FOR BOTH BANDIT INSTANCES
        for i in range(2):
            for arm in range(self.num_arms):
                self.values[i][arm] = np.random.beta(self.success[i][arm] + 1, self.fail[i][arm] + 1)
        val = (self.values[0] + self.values[1])/2           # Taking average of both samples for each arm
        return np.argmax(val)
        # END EDITING HERE
    
    def get_reward(self, arm_index, set_pulled, reward):
        # START EDITING HERE
        if reward == 0:
            self.fail[set_pulled][arm_index] += 1
        else:
            self.success[set_pulled][arm_index] += 1
        # END EDITING HERE

