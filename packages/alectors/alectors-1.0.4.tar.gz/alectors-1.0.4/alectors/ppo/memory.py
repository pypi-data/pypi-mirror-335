import torch
import numpy as np

class Memory:
    def __init__(
        self,
        batch_size
    ):
        self.batch_size = batch_size

        self.states = []
        self.actions = []
        self.probs = []
        self.vals = []
        self.rewards = []
        self.dones = []

    def recall(self):
        n_states = len(self.states)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states)
        np.random.shuffle(indices)
        batches = [
            indices[i:i + self.batch_size]
            for i in batch_start
        ]

        return np.array(self.states), \
            np.array(self.actions), \
            np.array(self.probs), \
            np.array(self.vals), \
            np.array(self.rewards), \
            np.array(self.dones), \
            batches
    
    def store(
        self,
        state,
        action,
        prob,
        val,
        reward,
        done
    ):
        self.states.append(state)
        self.actions.append(action)
        self.probs.append(prob)
        self.vals.append(val)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear(self):
        self.states = []
        self.actions
        self.probs = []
        self.vals = []
        self.rewards = []
        self.dones = []
