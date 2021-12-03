from data_structures import Gate
from data_structures import Pad
from data_structures import Net
from math import inf

def summation_of_HPWL(net_list, gate_list, pad_list):
    L = 0
    for i in range(len(net_list)):
        net_iter: Net = net_list[i]
        x_min = inf
        x_max = -inf
        y_min = inf
        y_max = -inf
        # consider gate coordinates
        for j in range(len(net_iter.connected_gates)):
            gate_number = net_iter.connected_gates[j]
            gate_iter: Gate = gate_list[gate_number-1]
            gate_coordinate = gate_iter.coordinate
            if gate_coordinate[0] < x_min:
                x_min = gate_coordinate[0]
            if gate_coordinate[0] > x_max:
                x_max = gate_coordinate[0]
            if gate_coordinate[1] < y_min:
                y_min = gate_coordinate[1]
            if gate_coordinate[1] > y_max:
                y_max = gate_coordinate[1]
        # consider pad coordinates
        for j in range(len(net_iter.connected_pad)):
            pad_number = net_iter.connected_pad[j]
            pad_iter: Pad = pad_list[pad_number-1]
            pad_coordinate = pad_iter.coordinate
            if pad_coordinate[0] < x_min:
                x_min = pad_coordinate[0]
            if pad_coordinate[0] > x_max:
                x_max = pad_coordinate[0]
            if pad_coordinate[1] < y_min:
                y_min = pad_coordinate[1]
            if pad_coordinate[1] > y_max:
                y_max = pad_coordinate[1]

        L += x_max - x_min + y_max - y_min

    return L
