from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy import sparse
from data_structures import *
import visualization
from parser import parser
from evaluations import summation_of_HPWL


def solve(net_list, gate_list, pad_list):
    # net_list, gate_list, pad_list = parser("benchmarks/3QP/test.txt")
    # # init_coordinate
    # for i in range(len(gate_list)):
    #     gate_list[i].coordinate = [random.randint(0, 100), random.randint(0, 100)]

    # 1. make C matrix
    size = len(gate_list)
    connected_info = []
    for i in range(len(net_list)):
        neighbor_gate_list = net_list[i].connected_gates
        for j in range(len(neighbor_gate_list)):
            for k in range(len(neighbor_gate_list)):
                if j != k:
                    connected_info.append([neighbor_gate_list[j], neighbor_gate_list[k], 1])
    del neighbor_gate_list, i, j, k
    connected_info = np.array(connected_info)
    connected_info2 = np.array(connected_info[:, 2], dtype=np.float64)
    connected_info0 = np.array(connected_info[:, 0], dtype=int)
    connected_info1 = np.array(connected_info[:, 1], dtype=int)

    C = coo_matrix((connected_info2, (connected_info0, connected_info1)))
    C = C.toarray()
    C = C[1:, 1:]
    del connected_info, connected_info0, connected_info1, connected_info2

    # 2. make A matrix
    A = np.zeros((size, size), dtype=np.float64)
    A = A + C
    for i in range(len(gate_list)):
        A[i][i] = -sum(C[i, :])
    A = -A

    for i in range(len(pad_list)):
        net_idx = pad_list[i].connected_net - 1
        connected_gates = net_list[net_idx].connected_gates
        for j in range(len(connected_gates)):
            gate_num = connected_gates[j]
            A[gate_num - 1][gate_num - 1] += 1

    # 3. get bx and by
    R = []
    C = []
    V = []
    for i in range(len(pad_list)):
        pad = pad_list[i]
        net_idx = pad.connected_net
        connected_net_i = net_list[net_idx - 1]
        gate_number = connected_net_i.connected_gates[0]  # this net has only one connection with pad and gate
        R.append(gate_number)
        R.append(gate_number)
        C.append(0)
        C.append(1)
        V.append(pad.coordinate[0])
        V.append(pad.coordinate[1])
    b = coo_matrix((V, (R, C)), shape=(size + 1, 2))  ## ??? why the size should be plused one
    b = b.toarray()
    b = b[1:, :]  # this is bx and by
    del V, R, C, i, j, net_idx, pad, connected_net_i, gate_number

    # 4. transform numpy array to coo_matrix and get x and y
    sA = sparse.csr_matrix(A)
    x_y = spsolve(sA.tocsr(), b)
    del A, sA, b
    x = x_y[:, 0]
    y = x_y[:, 1]
    for i in range(len(gate_list)):
        gate = gate_list[i]
        gate.set_coordinate(x_y[i])
    del gate, i, x_y

    return net_list, gate_list, pad_list


def sort_gates(gate_list):
    gate_list = sorted(gate_list, key=lambda gate: gate.benchmark_for_order)
    return gate_list


def main():
    benchmarks = ["benchmarks/toy1", "benchmarks/toy2", "benchmarks/primary1", "benchmarks/fract", "benchmarks/struct",
                  "benchmarks/biomed"]
    for bench_name in benchmarks:
        net_list, gate_list, pad_list = parser(bench_name)
        initial_HPWL = summation_of_HPWL(net_list, gate_list, pad_list)
        print("initial HPWL of", bench_name, initial_HPWL)
        net_list, gate_list, pad_list = solve(net_list, gate_list, pad_list)
        final_HPWL = summation_of_HPWL(net_list, gate_list, pad_list)
        print("FINAL HPWL of", bench_name, final_HPWL)
        print("delta HPWL of", bench_name, initial_HPWL - final_HPWL)
        visualization.draw_window(pad_list, gate_list, net_list, ver="Q", information=[bench_name])
        print()


if __name__ == "__main__":
    main()
