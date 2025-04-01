import numpy as np
import torch
from DQN import DQN  # Import the DQN class
import random
class AI_Agent:
    def __init__(self, dqn_model, device=torch.device("cpu"),train=True):
        self.dqn_model = dqn_model.to(device)
        self.device = device
        self.train = train
        #epsilon_start, epsilon_final, epsiln_decay = 1, 0.01, 5000

    def epsilon_greedy(self,epoch, start = 1, final=0.01, decay=5000):
        # res = final + (start - final) * math.exp(-1 * epoch/decay)
        if epoch < decay:
            return start - (start - final) * epoch/decay
        return final
    
    def getAction(self, state, epoch = 0, events= None, train = True):
        """Get the action based 
        on the DQN output."""
        # self.dqn_model.eval()
        # with torch.no_grad():
        #     state_tensor = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        #     q_values = self.dqn_model(state_tensor).cpu().numpy()[0]
        #     action_index = np.argmax(q_values)
        #     return action_index
        actions = [-1,0,1]
        if self.train and train:
            epsilon = self.epsilon_greedy(epoch)
            rnd = random.random()
            if rnd < epsilon:
                return random.choice(actions)
        
        with torch.no_grad():
            Q_values = self.dqn_model(state)
        max_index = torch.argmax(Q_values)
        return actions[max_index]
    
    def fix_update (self, dqn, tau=0.001):
        self.dqn_model.load_state_dict(dqn.state_dict())

    def Q (self, states, actions):
        Q_values = self.dqn_model(states) # try: Q_values = self.DQN(states).gather(dim=1, actions) ; check if shape of actions is [-1, 1] otherwise dim=0
        rows = torch.arange(Q_values.shape[0]).reshape(-1,1)
        cols = actions.reshape(-1,1)
        return Q_values[rows, cols]
    
    def get_Actions_Values (self, states):
        with torch.no_grad():
            Q_values = self.dqn_model(states)
            max_values, max_indices = torch.max(Q_values,dim=1) # best_values, best_actions
        
        return max_indices.reshape(-1,1), max_values.reshape(-1,1)