import numpy as np
import pandas as pd

class QLearningModel:
 def __init__(self, state_space_size, action_space, learning_rate, discount_factor, epsilon, q_table=None):
     self.action_space = action_space
     self.learning_rate = learning_rate
     self.discount_factor = discount_factor
     self.epsilon = epsilon
     self.q_table = q_table if q_table is not None else pd.DataFrame(data=np.zeros((state_space_size, len(action_space))),
                                                                      index=np.arange(state_space_size),
                                                                      columns=action_space)
 # This method decides the next action to take based on the current state and the Q-table.
 def decide_action(self, state):
     if np.random.rand() < self.epsilon:
         # Exploration: With probability epsilon, we choose a random action to explore new strategies.
         return np.random.choice(self.action_space)
     else:
         # Exploitation: With probability 1 - epsilon, we choose the best-known action based on the Q-table.
         return self.q_table.loc[state].idxmax()

 # This method updates the Q-table using the Q-learning algorithm after an action is taken.
 def learn(self, current_state, action, reward, next_state):
     # We first determine the best action to take in the next state based on the current Q-table.
     best_next_action = self.q_table.loc[next_state].idxmax()
     # The temporal difference (TD) target is the observed reward plus the discounted value of the next state.
     td_target = reward + self.discount_factor * self.q_table.loc[next_state, best_next_action]
     # The TD error is the difference between the TD target and the current Q-value.
     td_error = td_target - self.q_table.loc[current_state, action]
     # We update the Q-value for the current state and action using the TD error and the learning rate.
     self.q_table.loc[current_state, action] += self.learning_rate * td_error

# Define the state space size and action space for external access
state_space_size = 100  # This should be the number of possible states
action_space = ['buy', 'sell', 'hold']
learning_rate = 0.01
discount_factor = 0.9
epsilon = 0.1

