import random
import numpy as np


class Gate:
    def __init__(self, gate_id, connectivity):
        self.id = gate_id
        self.connectivity = connectivity
        self.connected_nets = []
        self.coordinate = np.array([random.randint(0, 1000) / 10, random.randint(0, 1000) / 10])
        # variables for FD algorithm
        self.status = 0  # 0 means unmoved
        self.connected_cell_number = 0
        self.force = np.array([0, 0])
        self.velocity = np.array([0, 0])
        self.mass = 17

    def reformat_data_type(self):
        for i in range(len(self.connected_nets)):
            self.connected_nets[i] = int(self.connected_nets[i])
        self.connectivity = int(self.connectivity)
        self.id = int(self.id)

    def set_coordinate(self, coordinate):
        self.coordinate = coordinate
        self.benchmark_for_order = 100000 * self.coordinate[0] + self.coordinate[1]


class Pad:
    def __init__(self, pad_number, connected_net, x, y):
        self.pad_number = pad_number
        self.connected_net = connected_net
        self.coordinate = np.array([x, y])

    def reformat_data_type(self):
        self.pad_number = int(self.pad_number)
        self.connected_net = int(self.connected_net)


class Net:
    def __init__(self, net_number):
        self.net_number = net_number
        self.connected_gates = []
        self.connected_pad = []

    def reformat_data_type(self):
        self.net_number = int(self.net_number)
        for i in range(len(self.connected_gates)):
            self.connected_gates[i] = int(self.connected_gates[i])
        for i in range(len(self.connected_pad)):
            self.connected_pad[i] = int(self.connected_pad[i])
