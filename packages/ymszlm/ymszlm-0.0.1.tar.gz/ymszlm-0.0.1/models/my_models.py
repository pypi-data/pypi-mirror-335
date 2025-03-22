import torch
from blackd.middlewares import F
from torch import nn


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(in_features=784, out_features=128)
        self.fc2 = nn.Linear(in_features=784, out_features=128)
        self.fc3 = nn.Linear(in_features=784, out_features=128)

    def forward(self, x):
        out1 = F.relu(self.fc1(x))
        out2 = F.relu(self.fc2(x))
        out3 = F.relu(self.fc3(x))
        return out1, out2, out3
