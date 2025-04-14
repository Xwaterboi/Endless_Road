import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

# Parameters
input_size = 5 # Q(state) see environment for state shape
layer1 = 128
layer2 = 128
output_size = 3# Q(state)-> value of a
gamma = 0.99 
 

class DQN (nn.Module):
    def __init__(self, device = torch.device('cpu')) -> None:
        super().__init__()
        self.device = device
        self.linear1 = nn.Linear(input_size, layer1,device=device)
        self.linear2 = nn.Linear(layer1, layer2,device=device)
        self.linear3 = nn.Linear(layer1, layer2,device=device)
        self.output = nn.Linear(layer2, output_size,device=device)
        #self.MSELoss = nn.MSELoss()
        self.HuberLoss = nn.SmoothL1Loss()

    def forward (self, x):
        x=x.to(self.device)
        x = self.linear1(x)
        x = F.leaky_relu(x)
        x = self.linear2(x)
        x = F.leaky_relu(x)
        x = self.linear3(x)
        x = F.leaky_relu(x)
        # x = self.linear4(x)
        # x = F.leaky_relu(x)
        # x = self.linear5(x)
        # x = F.leaky_relu(x)
        x = self.output(x)
        return x
    
    def loss (self, Q_values, rewards, Q_next_Values, dones ):
        Q_new = rewards.to(self.device) + gamma * Q_next_Values.to(self.device) * (1- dones.to(self.device))
        Q_new=torch.clamp(Q_new,-10,10)
        return self.HuberLoss(Q_values, Q_new)
    
    def load_params(self, path):
        self.load_state_dict(torch.load(path))

    def save_params(self, path):
        torch.save(self.state_dict(), path)

    def copy (self):
        return copy.deepcopy(self)

    def __call__(self, states):
        return self.forward(states).to(self.device)