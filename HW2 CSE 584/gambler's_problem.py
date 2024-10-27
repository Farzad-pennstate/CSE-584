# -*- coding: utf-8 -*-
"""Gambler's problem.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZLZOtcLZNLabH8gtp1v0VtlauA66ZhXM
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from google.colab import files

def one_step_lookahead(s, V, rewards):
  """
  Helper function to calculate the value for all action in a given state.

  Args:
    s: The gambler’s capital. Integer.
    V: The vector that contains values at each state.
    p_h: The probability of gambler winning the bet.
    rewards: The reward vector.

    Returns:
    A vector containing the expected value of each action.
    Its length equals to the number of actions.
  """
  p_h= 0.25
  A = np.zeros(101)
  stakes = range(1, min(s, 100-s)+1) # Your minimum bet is 1, maximum bet is min(s, 100-s).
  for a in stakes:
    # rewards[s+a], rewards[s-a] are immediate rewards.
    # V[s+a], V[s-a] are values of the next states.
    # This is the core of the Bellman equation: The expected value of your action is
    # the sum of immediate rewards and the value of the next state.
    A[a] = p_h * (rewards[s+a] + V[s+a]*discount_factor) + (1-p_h) * (rewards[s-a] + V[s-a]*discount_factor)
  return A

# The reward is zero on all transitions except those on which the gambler reaches his goal,
# when it is +1.
rewards = np.zeros(101)
rewards[100] = 1
# We introduce two dummy states corresponding to termination with capital of 0 and 100
V = np.zeros(101)
discount_factor = 1
theta = 0.0001
while True:
  # Stopping condition
  delta = 0
  # Update each state...
  for s in range(1, 100):
    # Do a one-step lookahead to find the best action
    A = one_step_lookahead(s, V, rewards)
    # print(s,A,V) # if you want to debug.
    best_action_value = np.max(A)
    # Calculate delta across all states seen so far
    delta = max(delta, np.abs(best_action_value - V[s]))
    # Update the value function. Ref: Sutton book eq. 4.10.
    V[s] = best_action_value
    # Check if we can stop
  if delta < theta:
    break

# Create a deterministic policy using the optimal value function
policy = np.zeros(100)
for s in range(1, 100):
  # One step lookahead to find the best action for this state
  A = one_step_lookahead(s, V, rewards)
  best_action = np.argmax(A)
  # Always take the best action
  policy[s] = best_action

print("Optimized Policy:")
print(policy)
print("")

print("Optimized Value Function:")
print(V)
print("")

# Plotting Final Policy (action stake) vs State (Capital)

# x axis values
x = range(100)
# corresponding y axis values
y = V[:100]

# plotting the points
plt.plot(x, y)

# naming the x axis
plt.xlabel('Capital')
# naming the y axis
plt.ylabel('Value Estimates')

# giving a title to the graph
plt.title('Final Policy (action stake) vs State (Capital)')

# function to show the plot
plt.show()

# Plotting Capital vs Final Policy

# x axis values
x = range(100)
# corresponding y axis values
y = policy

# plotting the bars
plt.bar(x, y, align='center', alpha=0.5)

# naming the x axis
plt.xlabel('Capital')
# naming the y axis
plt.ylabel('Final policy (stake)')

# giving a title to the graph
plt.title('Capital vs Final Policy')

# function to show the plot
plt.show()