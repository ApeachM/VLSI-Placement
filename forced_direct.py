import math

from data_structures import *
import parser
import visualization
import evaluations
import numpy as np


def is_all_moved(gate_list):
    status_checker = 1
    for i in range(len(gate_list)):
        gate_iter: Gate = gate_list[i]
        status_checker = status_checker * gate_iter.status
    if status_checker == 1:
        # all cell is moved
        return 1
    else:
        # some cell is not moved
        return 0


def extract_maxDegree_unmoved_cell(gate_list):
    idx = -1
    max_degree = -1
    consider_only_definition = 0
    for i in range(len(gate_list)):
        gate_iter: Gate = gate_list[i]
        if consider_only_definition == 1:
            if gate_iter.connectivity > max_degree and gate_iter.status == 0:
                max_degree = gate_iter.connectivity
                max_degree = gate_iter.connected_cell_number
                idx = i
        else:
            # considering the connected cell number instead of the definition of node degree
            if gate_iter.connected_cell_number > max_degree and gate_iter.status == 0:
                max_degree = gate_iter.connected_cell_number
                idx = i

    return gate_list[idx]


def ZFT_position(gate: Gate, gate_list, net_list, pad_list):
    connected_nets = gate.connected_nets
    sigma_cx = 0
    sigma_cy = 0
    sigma_c = gate.connected_cell_number  # because the weights of edge are all 1

    for i in range(len(connected_nets)):
        net_i: Net = net_list[connected_nets[i] - 1]
        for j in range(len(net_i.connected_gates)):
            gate_i = gate_list[net_i.connected_gates[j] - 1]
            xj = gate_i.coordinate[0]
            yj = gate_i.coordinate[1]
            sigma_cx += xj
            sigma_cy += yj
        for j in range(len(net_i.connected_pad)):
            pad_i = pad_list[net_i.connected_pad[j] - 1]
            xj = pad_i.coordinate[0]
            yj = pad_i.coordinate[1]
            sigma_cx += xj
            sigma_cy += yj
    xi = sigma_cx / sigma_c
    yi = sigma_cy / sigma_c

    return [xi, yi]


def relocate():
    pass


def forced_directed_placement(net_list, gate_list, pad_list):
    # arbitrary initial placement is already completed.
    # loc = LOCATIONS(p)
    loc = []
    for i in range(len(gate_list)):
        gate_i = gate_list[i]
        gate_coordinate = gate_i.coordinate.tolist()
        loc.append(gate_coordinate)
    # status is also already set by unmoved

    stop = 0
    N = 1
    # continue until all cells have been moved or some stopping criterion is reached
    while (not is_all_moved(gate_list) and not stop):
        # c = MAX_DEGREE(V, status)
        unmoved_max_degree_cell = extract_maxDegree_unmoved_cell(gate_list)
        # ZFT_pos = ZFT_position(c)
        ZFT_pos = ZFT_position(unmoved_max_degree_cell, gate_list, net_list, pad_list)

        # if position is unoccupied,
        if ZFT_pos not in loc:
            # move c to its ZFT position
            unmoved_max_degree_cell.coordinate = ZFT_pos
            loc[unmoved_max_degree_cell.id - 1] = ZFT_pos
        else:
            # RELOCAE(c, loc)
            relocate()
            # temporal code
            unmoved_max_degree_cell.coordinate = ZFT_pos
            loc[unmoved_max_degree_cell.id - 1] = ZFT_pos

        # status[c] = MOVED
        unmoved_max_degree_cell.status = 1
        # visualization.draw_window(pad_list, gate_list, net_list, FD=1, remark=N)
        visualization.draw_window(pad_list, gate_list, net_list)
        N += 1


def get_forces(net_list, gate_list, pad_list):
    # get the all gate positions as numpy arrray
    positions = np.zeros((len(gate_list), 2))
    for i in range(len(gate_list)):
        gate_i: Gate = gate_list[i]
        coordinate = np.array(gate_i.coordinate)
        positions[i] = coordinate

    for i in range(len(gate_list)):

        # print(i)
        gate_i = gate_list[i]
        force = np.zeros(2)
        gate_i_coordinate = np.array(gate_i.coordinate)

        # get the hook forces
        # connected_cell_positions = np.zeros((len(gate_i.connected_cell_number), 2))
        for j in range(len(gate_i.connected_nets)):
            net_i: Net = net_list[gate_i.connected_nets[j] - 1]
            for k in range(len(net_i.connected_gates)):
                connected_gate_i: Gate = gate_list[net_i.connected_gates[k] - 1]
                connected_gate_i_coordinate = np.array(connected_gate_i.coordinate)
                force = force + (connected_gate_i_coordinate - gate_i_coordinate)
            for k in range(len(net_i.connected_pad)):
                connected_pad_i: Pad = pad_list[net_i.connected_pad[k] - 1]
                connected_pad_i_coordinate = np.array(connected_pad_i.coordinate)
                force = force + (connected_pad_i_coordinate - gate_i_coordinate)

        # get the repulsive forces
        repulsive_coefficient = 150 # this value should consider the number of cells
        temp = np.ones((len(gate_list), 2)) * gate_i.coordinate
        displacements = positions - temp
        denominators = np.hypot(displacements[:, 0], displacements[:, 1]) ** 2
        denominators = np.reshape(denominators, (len(gate_list), 1))
        denominators = np.concatenate((denominators, denominators), axis=1)

        repulsive_forces = -displacements / denominators

        repulsive_force = np.nansum(repulsive_forces, axis=0) / ((len(gate_list)) / repulsive_coefficient)
        force = force + repulsive_force

        # force update
        gate_i.force = force - 20 * gate_i.velocity  # consider the friction


def move(net_list, gate_list, pad_list):
    unit_time = 0.5
    activity = 0
    for i in range(len(gate_list)):
        gate_i: Gate = gate_list[i]
        # velocity update
        gate_i.velocity = gate_i.velocity + (gate_i.force / gate_i.mass) * unit_time
        # position update
        gate_i.coordinate = gate_i.coordinate + gate_i.velocity * unit_time
        if gate_i.coordinate[0] > 100:
            gate_i.coordinate[0] = 100
        if gate_i.coordinate[1] > 100:
            gate_i.coordinate[1] = 100
        if gate_i.coordinate[0] < 0:
            gate_i.coordinate[0] = 0
        if gate_i.coordinate[1] < 0:
            gate_i.coordinate[1] = 0

        # check activity
        activity += gate_i.velocity
    activity /= len(gate_list)
    return activity


def forced_directed_placement_with_repulsive_force(net_list, gate_list, pad_list):
    N = 0
    HPWL_list = []
    # while True:
    for i in range(300):
        print(i)
        get_forces(net_list, gate_list, pad_list)
        activity = move(net_list, gate_list, pad_list)
        # visualization.draw_window(pad_list, gate_list, net_list, FD=1, remark=N)
        visualization.draw_window(pad_list, gate_list, net_list, remark=N, path="FD_images")
        HPWL = evaluations.summation_of_HPWL(net_list, gate_list, pad_list)
        HPWL_list.append(HPWL)
        print(HPWL)
        # if len(HPWL_list) > 10:
        #     if HPWL_list[-4] - HPWL_list[-1] < HPWL_list[1] - HPWL_list[2] / 10000:
        #         break
        N += 1


def main():
    benchmarks = ["benchmarks/toy1", "benchmarks/toy2", "benchmarks/primary1", "benchmarks/fract", "benchmarks/struct",
                  "benchmarks/biomed"]


    net_list, gate_list, pad_list = parser.parser("benchmarks/struct")
    print(evaluations.summation_of_HPWL(net_list, gate_list, pad_list))
    visualization.draw_window(pad_list, gate_list, net_list, ver="FD1")
    # forced_directed_placement(net_list, gate_list, pad_list)
    forced_directed_placement_with_repulsive_force(net_list, gate_list, pad_list)
    visualization.draw_window(pad_list, gate_list, net_list, ver="FD2")
    print(evaluations.summation_of_HPWL(net_list, gate_list, pad_list))


if __name__ == "__main__":
    main()
    visualization.pygame_quit(save_image=1)
    print("end")
