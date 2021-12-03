from data_structures import *


def parser(filename):
    # parse the txt file
    file = open(filename)
    lines = file.readlines()
    file.close()
    file_info = []
    for line in lines:
        line = line.strip()
        line = line.split()
        for i in range(len(line)):
            line[i] = float(line[i])

        file_info.append(line)
    del line, lines, file

    # parse the info of gates and nets
    gate_number = int(file_info[0][0])
    net_number = int(file_info[0][1])
    gate_list = []
    file_info.pop(0)

    for i in range(gate_number):
        gate_info = file_info.pop(0)
        temp_gate = Gate(gate_info[0], gate_info[1])
        for j in range(int(temp_gate.connectivity)):
            temp_gate.connected_nets.append(gate_info.pop(2))
        temp_gate.reformat_data_type()
        gate_list.append(temp_gate)
    del gate_info, i, j, temp_gate

    # parse the pad info
    pad_number = int(file_info.pop(0)[0])
    pad_list = []
    for i in range(pad_number):
        pad_info = file_info.pop(0)
        temp_pad = Pad(pad_info[0], pad_info[1], pad_info[2], pad_info[3])
        temp_pad.reformat_data_type()
        pad_list.append(temp_pad)
    del i, temp_pad, pad_info, file_info

    # generate the net list
    net_list = []  # None is for the equality of index and net ID
    for i in range(net_number):
        net_list.append(Net(i + 1))
    for i in range(gate_number):
        temp_gate = gate_list[i]
        temp_connection_list = temp_gate.connected_nets
        for j in range(temp_gate.connectivity):
            net_list[temp_connection_list[j] - 1].connected_gates.append(temp_gate.id)
    del temp_gate, temp_connection_list, i, j
    for i in range(pad_number):
        temp_pad = pad_list[i]
        connected_net = temp_pad.connected_net
        net_list[connected_net - 1].connected_pad.append(temp_pad.pad_number)
    del temp_pad, connected_net, i

    for i in range(len(net_list)):
        net_list[i].reformat_data_type()

    # get the connected_cell_number
    for i in range(len(gate_list)):
        gate_i = gate_list[i]
        connected_nets = gate_i.connected_nets
        for j in range(len(connected_nets)):
            net_i = net_list[connected_nets[j]-1]
            gate_i.connected_cell_number += len(net_i.connected_gates)
            gate_i.connected_cell_number += len(net_i.connected_pad)


    # for equality with indexing and ID
    # net_list.insert(0, None)
    # gate_list.insert(0, None)
    # pad_list.insert(0, None)
    return net_list, gate_list, pad_list
