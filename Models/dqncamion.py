# In this program we will use a DQN to train an agent to fill the truck with the best possible items

import numpy as np
import random
import os
import pandas as pd
import plotly.express as px
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class DQNCamion(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DQNCamion, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class DQNTruckTypeAgent:
    def __init__(self):
        self.model = DQNCamion(2, 256, 2)
        self.target_model = DQNCamion(2, 256, 2)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.loss = nn.MSELoss()
        self.memory = []
        self.gamma = 0.9
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9999
        self.batch_size = 32
        self.target_update_counter = 0
        self.update_target_model()

    def get_state(self, dI):
        state = []
        state.append(list(dI.amount_needed.values))
        for t in range(dI.days_stock_coverage):
            for i in dI.products:
                state.append(dI.dicc_demanda[(i, dI.t + t)])
        return state

    def take_action(self, dI):
        if np.random.rand() <= self.epsilon:
            action = random.randrange(2)
        else:
            state = self.get_state(dI)
            state = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state)
            action = torch.argmax(prediction).item()
        dI.trucks_per_day[dI.t].append(Truck(action))
        dI.current_truck = dI.trucks_per_day[dI.t][-1]


        return action


class DQNTruckLoadingAgent:
    def __init__(self):
        self.model = DQNCamion(2, 256, 2)
        self.target_model = DQNCamion(2, 256, 2)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.loss = nn.MSELoss()
        self.memory = []
        self.gamma = 0.9
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9999
        self.batch_size = 32
        self.target_update_counter = 0
        self.update_target_model()


    def get_state(self, dI):
        state = []
        state.append(list(dI.amount_needed.values))
        for t in range(dI.days_stock_coverage):
            for i in dI.products:
                state.append(dI.dicc_demanda[(i, dI.t + t)])
        return state
class Truck:
    def __init__(self, boxes_type_a, boxes_type_b, max_a_col,max_b_col , dims_truck, num_rows):
        self.boxes_type_a = boxes_type_a
        self.boxes_type_b = boxes_type_b
        self.index_boxes=["a","b"]
        self.max_a_col = max_a_col
        self.max_b_col = max_b_col
        self.dims_truck = dims_truck
        self.num_rows = num_rows
        self.loading= { (r,c,"a"): {h: None for h in range(max_a_col)} for r in range(num_rows) for c in range(boxes_type_a)}
        self.loading.update({ (r,c,"b"): {h: None for h in range(max_b_col)} for r in range(num_rows) for c in range(boxes_type_b)})



class DemandInformation:
    def __init__(self, products, types_of_containers, days, dicc_containers, dicc_demanda, dicc_trucks, dicc_stock_day1, days_stock_coverage):

        # This are the set of indices
        self.products = products
        self.types_of_containers = types_of_containers
        self.days = days

        # Set of parameters
        self.dicc_containers = dicc_containers
        self.dicc_demanda = dicc_demanda
        self.dicc_trucks = dicc_trucks
        self.dicc_stock_day1 = dicc_stock_day1

        # Set of variables

        self.dicc_stock = {p: {d: None for d in days} for p in products}
        self.trucks_per_day = {d: [] for d in days}
        self.amount_needed = { p: dicc_stock_day1[p]-sum(dicc_demanda[p][days[0]]+range(days_stock_coverage+1) )for p in products}
        self.t=0


