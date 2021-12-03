import math

import numpy
import numpy as np

import visualization
from visualization import print_pads_and_gates
from data_structures import Gate
from data_structures import Pad
from data_structures import Net
from evaluations import summation_of_HPWL
import random
import parser
import pandas as pd


def simulated_annealing(net_list, gate_list, pad_list):
    remark = 0
    # initializing temperature
    N = 1
    T = 0.5
    frozen = False

    HPWL_list = []

    HPWL_list.append(summation_of_HPWL(net_list, gate_list, pad_list))
    HPWL_list_raw = np.array(HPWL_list)
    HPWL_min = np.inf
    while (not frozen):
        M = 5  # M is how many swaps per gate
        for n in range(M * len(gate_list)):
            L_before = summation_of_HPWL(net_list, gate_list, pad_list)

            # swap 2 random gates Gi and Gj
            i = random.randint(0, len(gate_list) - 1)
            j = random.randint(0, len(gate_list) - 1)
            Gi: Gate = gate_list[i]
            Gj: Gate = gate_list[j]

            Gi_coordinate = Gi.coordinate
            Gj_coordinate = Gj.coordinate
            Gi.coordinate = Gj_coordinate
            Gj.coordinate = Gi_coordinate

            # compute delta L
            L_after = summation_of_HPWL(net_list, gate_list, pad_list)
            delta_L = L_after - L_before

            if delta_L < 0:
                # accept this swap
                pass
            else:
                if random.randint(0, 1000) / 1000 < math.exp(- delta_L / T):
                    pass
                    # accept this swap
                else:
                    # undo uphill swap
                    Gi.coordinate = Gi_coordinate
                    Gj.coordinate = Gj_coordinate
            HPWL_list_raw = numpy.append(HPWL_list_raw, L_after)
            remark += 1

            # visualization
            if L_after < HPWL_min:
                HPWL_min = L_after
                print(L_after)
                information = []
                information.append(T)
                information.append(L_after)
                visualization.draw_window(pad_list, gate_list, net_list, ver="SA", remark=remark,
                                          information=information)


        # if HPWL still decreasing over the last few temperatures
        HPWL_list.append(summation_of_HPWL(net_list, gate_list, pad_list))
        if len(HPWL_list) >= 10:
            if HPWL_list[-4] < HPWL_list[-1]:
                frozen = True
        T = 0.9 * T
        print()
        print("HPWL_list:", HPWL_list)

        N += 1
        df = pd.DataFrame(HPWL_list_raw)
        df.to_csv("HPWL_list_SA.csv", index=False)


def main():
    net_list, gate_list, pad_list = parser.parser("benchmarks/struct")
    simulated_annealing(net_list, gate_list, pad_list)


if __name__ == "__main__":
    main()
    print("end.")
