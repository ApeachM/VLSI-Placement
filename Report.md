# Global Placement of VLSI Physical Design

This document refers to a book theoughoutly, which name is *VLSI Physical Design: From Graph Partitioning to Timing Closure*. [1]

## 1. Introduction

### 1.1 Preamble

Integrated circuits (ICs) must be designed and optimized before new semiconductor chips may be manufactured. Modern chip design has gotten so sophisticated that it is mostly handled by specialized software that is updated on a regular basis to keep up with advances in semiconductor technology and increasing design complexities. This software requires a high-level grasp of the implemented algorithms from the user. A developer of this software, on the other hand, must have a solid computer science background, as well as a thorough understanding of how various algorithms work and interact, as well as where their performance bottlenecks are.

### 1.2 VLSI Physical Design

The below figure indicates the all over process of design VLSI, including Physical Design. Creating a very large-scale integrated (VLSI) circuit is a difficult task. As seen in the diagram below, it can be broken down into various steps. The earlier design steps are high-level, while the later design steps are at a lower abstraction level. Before fabrication, tools and algorithms act on extensive information about each circuit element's geometric shape and electrical properties at the end of the process. The physical design is the one of the step of VLSI implementation.

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0o4pq7gpj311b0u078e.jpg" alt="image-20211202141848500" style="zoom:50%;" />

All design components are instantiated with their geometric representations during physical design. In other words, per manufacturing layer, all macros, cells, gates, transistors, and other objects with fixed forms and sizes are allocated spatial locations (placement) and necessary routing connections (routing) are finished in metal layers. Physical design yields a set of production specifications that must be confirmed afterward.
Physical design is done in accordance with design guidelines that describe the fabrication medium's physical restrictions. For example, all cables must be spaced a certain distance apart and have a certain width. As a result, each new manufacturing method necessitates re-creating (migrating) the original layout.

#### 1.2.1 VLSI Physical Design Processes

As above figure, Physical design is divided into several main processes because of its tremendous complexity.

- *Partitioning* divides a circuit into smaller subcircuits or modules, each of which can be constructed or evaluated separately.
- *Floorplanning* establishes the shapes and configurations of subcircuits or modules, as well as the locations of external ports and IP or macro blocks.
- *Power and ground routing* distributes power (*VDD*) and ground (*GND*) nets throughout the chip, and is typically an integral part of floorplanning.
- *Placement* determines the spatial locations of each block's cells.
- *Clock network synthesis* establishes how the clock signal is buffered, gated (for example, for power management), and routed to fulfill specified skew and delay criteria.
- *Global routing* allocates routing resources that are used for connections; for example, routing tracks in channels and switchboxes are examples of routing resources.
- *Detailed routing* assigns routes to individual metal layers.

#### 1.2.2 Global Placement and Detailed Placement

For big circuits, placement approaches include *global placement*, *detailed placement*, and legalization. Global placement frequently ignores the shapes and sizes of placeable items and fails to align their placements with appropriate grid rows and columns. Because the emphasis is on sensible global location and overall density distribution, some overlaps between placed objects are acceptable. Before or during detailed installation, legalization is conducted. It aims to align placeable objects with rows and columns, as well as remove overlap, while minimizing displacements from global placement sites, as well as connection length and circuit delay. By performing local actions (e.g., swapping two objects) or relocating multiple objects in a row to make way for another object, detailed placement improves the location of each standard cell progressively. Although global and detailed placement have similar runtimes, global placement frequently takes significantly more memory and is more difficult to parallelize. This document will mainly cover some of the *global placement* methods.

#### 1.2.3 Considerable Factors for VLSI Physical Design

Circuit performance, area, reliability, power, and manufacturing yield are all influenced by physical design. Below are some examples of these effects.

- Performance: Signal delays are substantially longer on long routes.
- Area: separating coupled modules results in larger and slower chips.
- Reliability: A large number of vias might impair the circuit's reliability dramatically.
- Power: lower gate length transistors enable faster switching speeds at the expense of increased leakage current and manufacturing variability; larger transistors and longer wires result in more dynamic power dissipation.
- Yield: wires routed too close together may reduce yield due to electrical shorts during manufacturing, but spreading gates too far apart may also reduce yield due to longer wires and a larger likelihood of openings.

#### 1.2.4 Limitaions for VLSI Physical Design

Three types of limitations must be addressed during physical design.

- Technology constraints are derived from technology restrictions and permit fabrication for a certain technology node. Minimum layout widths and spacing values between layout shapes are two examples.
- Electrical restrictions guarantee the design's desired electrical behavior. Meeting maximum signal delay timing limitations and staying below maximum coupling capacitances are two examples.
- Geometry (design methodology) restrictions are added to lessen the design process' overall complexity. The use of preferred wiring paths during routing and the positioning of standard cells in rows are two examples

### 1.3 Topic and Purpose of Reseach

We will focus on the Global Placement of Placement in the above VLSI design processes, and implement several methods of that. By a specific evaluation method like HPWL (that will be described below) and time, we will compare the performances of the several global placement methods.

## 2. Heuristic Global Placement Methods (Main Subject)

We will implementation three heuristic global placement methods, one is *Quadratic placement*, another is *Simulated Annealing*, the other is *Force-Directed Placement*.

![image-20211202153534596](https://tva1.sinaimg.cn/large/008i3skNgy1gwzh9w3ja3j315k0f80ut.jpg)

### 2.1 Prepare for the Placement

#### 2.1.1 Data structures

And below code is `data_structures.py`, which is used above code and contains the Gate, Pad, Net data structure considering benchmarks.

```python
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
        self.mass = 10

    def reformat_data_type(self):
        for i in range(len(self.connected_nets)):
            self.connected_nets[i] = int(self.connected_nets[i])
        self.connectivity = int(self.connectivity)
        self.id = int(self.id)

    # function for Quadratic Placement
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

```



#### 2.1.2 Benchmarks

We'll use the benchmarks from the Assignment 3 of [VLSI CAD Part II: Layout](https://www.coursera.org/learn/vlsi-cad-layout) Class in *Coursera* which professor name is [Rob A. Rutenbar](https://www.coursera.org/learn/vlsi-cad-layout#instructors). 

This is the example which file name is "toy1".

```text
18 20   
1 2 20 19      
2 2 2 1       
3 2 1 18
4 3 3 4 5       
5 6 6 5 4 3 7 8 
6 2 9 4
7 2 10 3
8 2 19 9
9 2 9 10
10 4 11 10 12 13 
11 2 12 16
12 2 7 6 
13 2 12 11 
14 2 14 17
15 2 8 15 
16 5 15 16 17 18 7 
17 4 16 17 18 14 
18 5 13 16 17 18 12
6              
1 12 25 0   
2 17 50 100    
3 18 100 50       
4 2 0 50      
5 19 0 25      
6 20 75 100
```

The first line, `line 1` indicates the number of gates and the number of nets. Here, the number of gates is 18 and the number of gate is 20.
From `line 2 ~ line 19` indicates the gate informations, which is the gate connectivity with nets. For example, in the `line 2`, we can know the `Gate 1` is connected with two Nets, which are `Net 20` and `Net 19`. In the `line 11`, we can know the `Gate 10` is connected with 4 Nets, which are `Net 11`, `Net 10`, `Net 12`, and `Net 13`. 
After the gate informations, the `line 20` `(20 = 1 + number of gates)` indicates the Pad number. Here, the pad number is six as `line 20` indicates. Below from there, each Net information indicates the connected Net number and the Pad coordinate. For example, in `line 26`, we can know `Pad 6` is connected with `Net 20` and the coordinate of `Pad 6`is (75, 100).

The name of bench marks are each `fract`, `primary`, `struct`, `toy1`, `toy2`, and `biomed`. We have 6 benchmarks.

For parsing this, we can implementation using the python as below. This file name is `parser.py`

```python
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
```



#### 2.1.3 Optimization Objectives (Evaluation Method)

The placer improves routing quality parameters such total weighted wire length, cut size, wire congestion (density), and maximum signal delay predictions (Figure 2.2.1).

The fundamental purpose of placement is to reduce delays along signal pathways. Because a net's latency is proportional to its length, placers try to keep overall wirelength to a minimum. As shown in below Figure 2.2.2, the placement of a design has a significant impact on net lengths and wire density. As we can see, the right placemet significantly reduce the total wire lengths than the left one.

| ![image-20211202184251798](https://tva1.sinaimg.cn/large/008i3skNgy1gx0o2kw2ykj31i40fejth.jpg) | ![image-20211202184545275](https://tva1.sinaimg.cn/large/008i3skNgy1gx0o2w0a31j312m0h8di2.jpg) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Figure 2.2.1                                                 | Figure 2.2.2                                                 |

The total wire length can impact the signal latency and performance, we set the objective function using this paramenter. Here, the *half-perimeter wirelength* (*HPWL*) model is commonly used because it is reasonably accurate and efficiently calculated. We can estimate the HPWL figure as below. In the below figure, the HPWL of "2-point net" is 5, and the one of "4-point net" is 7.

```
HPWL = [max{X coordinates of all gates) – min{X coordinates of all gates}] + [max{Y coordinates of all gates) – min{Y coordinates of all gates}]
```

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0o3eqxikj316o0esgoh.jpg" alt="image-20211202195024973" style="zoom:30%;" />

We can implement this using python. The code name is `evaluations.py`

```python
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
```

#### 2.1.4 Visualization

The  `pygame` package is used for visualization. The routing is not implemented in this project and only placement is implemented therefore, we can express the net as the lines from the centers of to connected cells.

For example, let the benchmark, which name is `test3` is below.

```
5 2
1 1 1
2 1 1
3 1 1
4 1 1
5 1 1
1
1 2 0 0
```

This means there're only five Gates and only one pad, and all the gate are connected to `Net1`. If we set the gate coordinates as below and do the visualization, then the result will be below figure.

```python
def visualization_example():
    net_list, gate_list, pad_list = parser.parser("benchmarks/test3")
    gate1 = gate_list[0]
    gate2 = gate_list[1]
    gate3 = gate_list[2]
    gate4 = gate_list[3]
    gate5 = gate_list[4]
    gate1.coordinate = [40, 10]
    gate2.coordinate = [60, 10]
    gate3.coordinate = [80, 10]
    gate4.coordinate = [40, 80]
    gate5.coordinate = [60, 80]
    draw_window(pad_list, gate_list, net_list, ver="visualization")
```

| Visualization Result<br /><br /><br /><br /><br /><br /><br /> | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0o49fij6j30uy0u0mxr.jpg" alt="image-20211202212848834" style="zoom:20%;" /> |
| :----------------------------------------------------------: | ------------------------------------------------------------ |

For each nets we can approach the gates and pads, and get the coordinates of them. By this method, we can draw one frame of the placement. The below code is the drawing function in the `visualization.py`.

```python
def draw_window(pad_list, gate_list, net_list):
    # get the coordinates and scale that.
    gate_coordinates = []
    pad_coordinates = []

    for i in range(len(gate_list)):
        gate_i: data_structures.Gate = gate_list[i]
        gate_coordinate = [int(gate_i.coordinate[0] * 10), int(gate_i.coordinate[1] * 10)]
        gate_coordinates.append(gate_coordinate)
    for i in range(len(pad_list)):
        pad_i: data_structures.Pad = pad_list[i]
        pad_coordinate = [int(pad_i.coordinate[0] * 10), int(pad_i.coordinate[1] * 10)]
        pad_coordinates.append(pad_coordinate)

    # get the net centers
    net_centers = []
    for i in range(len(net_list)):
        net_i: data_structures.Net = net_list[i]
        connected_gate_num = len(net_i.connected_gates)
        x_center = 0
        y_center = 0
        for j in range(connected_gate_num):
            gate_i = gate_list[net_i.connected_gates[j] - 1]
            x_center += gate_i.coordinate[0]
            y_center += gate_i.coordinate[1]

        connected_pad_num = len(net_i.connected_pad)
        for j in range(connected_pad_num):
            pad_i = pad_list[net_i.connected_pad[j] - 1]
            x_center += pad_i.coordinate[0]
            y_center += pad_i.coordinate[1]

        x_center = x_center / (connected_gate_num + connected_pad_num)
        y_center = y_center / (connected_gate_num + connected_pad_num)

        # scale
        x_center = int(x_center * 10)
        y_center = int(y_center * 10)
        net_center = [x_center, y_center]
        net_centers.append(net_center)

    # get the net line coordinates
    gate_coordinates_for_nets = []
    pad_coordinates_for_nets = []

    for i in range(len(net_list)):
        net_i: data_structures.Net = net_list[i]
        connected_gate_num = len(net_i.connected_gates)
        gate_coordinates_for_net_i = []
        for j in range(connected_gate_num):
            gate_i: data_structures.Gate = gate_list[net_i.connected_gates[j] - 1]
            gate_coordinate = [int(gate_i.coordinate[0] * 10), int(gate_i.coordinate[1] * 10)]  # scaled gate coordinate
            gate_coordinates_for_net_i.append(gate_coordinate)
        gate_coordinates_for_nets.append(gate_coordinates_for_net_i)

        connected_pad_num = len(net_i.connected_pad)
        pad_coordinates_for_net_i = []
        for j in range(connected_pad_num):
            pad_i: data_structures.Pad = pad_list[net_i.connected_pad[j] - 1]
            pad_coordinate = [int(pad_i.coordinate[0] * 10), int(pad_i.coordinate[1] * 10)]  # scaled coordinate
            pad_coordinates_for_net_i.append(pad_coordinate)
        pad_coordinates_for_nets.append(pad_coordinates_for_net_i)

    # delete the completely used variables
    del gate_coordinates_for_net_i, gate_coordinate, connected_gate_num, gate_i, i, j, net_center, x_center, y_center

    # for times in range(len(net_list)):
    for times in range(1):
        # print(times)
        clock.tick(100)
        screen.fill(WHITE)

        for i in range(len(net_list)):
            gate_coordinates_for_net_i = gate_coordinates_for_nets[i]
            pad_coordinates_for_net_i = pad_coordinates_for_nets[i]
            for j in range(len(gate_coordinates_for_net_i)):
                pygame.draw.line(screen, RED, net_centers[i], gate_coordinates_for_net_i[j])
            for j in range(len(pad_coordinates_for_net_i)):
                pygame.draw.line(screen, RED, net_centers[i], pad_coordinates_for_net_i[j])


        for i in range(len(gate_list)):
            pygame.draw.circle(screen, BLACK, gate_coordinates[i], 3)
        for i in range(len(pad_list)):
            pygame.draw.circle(screen, BLUE, pad_coordinates[i], 5)


        pygame.display.flip()
```



### 2.2 Global Placement Implementation

#### 2.4.1 Simulated Annealing

Simulated Annealing is most well known placement algorithm. Below is the pseudo code for this algorithm

![](https://tva1.sinaimg.cn/large/008i3skNgy1gwztod2czuj31hu0tq440.jpg)

Here, the cost can be expressed by HPWL, and `PERTURB(P)` is swapping the gate positions. Before explaining SA(Simulated Annealing), we should understand `Random Iterative Improvement Place`. Below is the pseudo code for that.

```
def random_iterative_improvement_place():
	// random initial placement 
	for each (gate Gi in gate_list):
		place Gi in random location (x,y) in grid not already occupied
	//calculate initial HPWL wirelength for whole netlist
	L = 0 
	for each (net Ni in net_list):
		L += HPWL(Ni)
	
	// main improvement loop
	while (overall HPWL wirelength L is improving):
		pick random Gi and Gj in gate_list
		swap the position of Gi and Gj
		evaluate delta_L = new HPWL - old HPWL
		if (delta_L < 0):
			// accept the swap and update HPWL
			L += HPWL
		else:
			// delta_L > 0 -> this means the swap makes it worse.
			undo swap of Gi and Gj
```

If the cost-solution graph has only one local minimum, then the above will work. However, generally it will not. The below figure indicates well the general situation of cost-solution function.

![image-20211202225815489](Report.assets/image-20211202225815489.png)

If we use only above code, the solution will be stagnant at the non-optimal solution. Therefore, we need tolerance for this. Now, we should consider how we can deal this tolerance. The solution of this can be found from SA algorithm. In SA algorithm, we accept the situations that require tolerance (when delta HPWL is positive) using the probability. The probability for accepting is determined by `Temperature`. If `Temperature` is hight, we accept the positive HPWL changes, and if `Temperature` is low, we hardly accept the positive HPWL. The below figure explains this well. 

![image-20211202231439564](https://tva1.sinaimg.cn/large/008i3skNgy1gwzujgl0ofj318m0g2q6p.jpg)

The probability which is determined by `Temperature` can be explained by below.
$$
probability = exp(\frac{-\Delta L}{T})
$$
Now, we can add this consideration to the `random_iterative_improvement_place`  code like below.

```
def SA():
	// random initial placement 
	for each (gate Gi in gate_list):
		place Gi in random location (x,y) in grid not already occupied
	//calculate initial HPWL wirelength for whole netlist
	L = 0 
	for each (net Ni in net_list):
		L += HPWL(Ni)
	
	// main improvement loop
	T = high temperature
	frozen = false
	while(!frozen):
    for i in range(M * len(gate_list)): // M is how many swaps-per-gate
      pick random Gi and Gj in gate_list
      swap the position of Gi and Gj
      evaluate delta_L = new HPWL - old HPWL
      if (delta_L < 0):
        // accept the swap and update HPWL
        L += HPWL
      else:
        // delta_L > 0 -> this means the swap makes it worse.
        //// mainly changed code ////
        if uniform_random(0, 1) < exp(-delta_L / T):
          then accept this 'uphill' swap
        /////////////////////////////		
        else:
          undo swap of Gi and Gj
    if HPWL(all_nets) still decreasing over the last few temperatures:
    	T = 0.9 * T
    else:
    	frozen = True
   
   return final placement as best solution
```

The python implementation is below. This function is from `SA.py`

```python
def simulated_annealing(net_list, gate_list, pad_list):
    # initializing temperature
    # T = HPWL(net_list, gate_list, pad_list)
    N = 1
    T = 0.5
    frozen = False

    HPWL_list = []
    while (not frozen):
        M = 5  # M is how many swaps per gate
        for n in range(M * len(gate_list)):
            L_before = summation_of_HPWL(net_list, gate_list, pad_list)

            # swap 2 random gates Gi and Gj
            i = random.randint(0, len(gate_list)-1)
            j = random.randint(0, len(gate_list)-1)
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
                    print(L_after)
                    pass
                else:
                    # undo uphill swap
                    Gi.coordinate = Gi_coordinate
                    Gj.coordinate = Gj_coordinate

        # if HPWL still decreasing over the last few temperatures
        HPWL_list.append(summation_of_HPWL(net_list, gate_list, pad_list))
        if len(HPWL_list) >= 10:
            HPWL_list = HPWL_list[-10:]
            if HPWL_list[-4] < HPWL_list[-1]:
                frozen = True
        T = 0.9 * T
        # print_pads_and_gates(pad_list, gate_list, N)
        print()
        print("T:", T)
        print("N:", N)
        print("HPWL_list:", HPWL_list)
        visualization.draw_window(pad_list, gate_list, net_list, SA=1, remark=N)
        N += 1
```





#### 2.4.2 Quadratic Placement

For implementation of Quadratic Placement, the course of [VLSI CAD Part II: Layout](https://www.coursera.org/learn/vlsi-cad-layout) Class in *Coursera* which professor name is [Rob A. Rutenbar](https://www.coursera.org/learn/vlsi-cad-layout#instructors) is all over refered.

The sqaured Euclidean distance can calculated by below. 

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0kphz21yj30w608i0t2.jpg" alt="image-20211203141949801" style="zoom:50%;" />

As summation of Euclidean distance, we can use this as the cost function of placement. The below figure can be good example. Here, we should minimize the summation of the distance value.

| Example                                                      | Minimize method for cost function                            |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0ks18bz0j31d40j4jv4.jpg" alt="image-20211203142230205" style="zoom:50%;" /> | ![image-20211203142653580](https://tva1.sinaimg.cn/large/008i3skNgy1gx0o5383d1j31es0fkgok.jpg) |

Here, we can minimize the cost function as derivative of cost function, which method is linear. As this method, we can implementation of this placement as below. Below function  is from `Quadratic.py` 

```python
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
        net_idx = pad_list[i].connected_nets - 1
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
        net_idx = pad.connected_nets
        connected_net = net_list[net_idx - 1]
        gate_number = connected_net.connected_gates[0]  # this net has only one connection with pad and gate
        R.append(gate_number)
        R.append(gate_number)
        C.append(0)
        C.append(1)
        V.append(pad.coordinate[0])
        V.append(pad.coordinate[1])
    b = coo_matrix((V, (R, C)), shape=(size + 1, 2))  ## ??? why the size should be plused one
    b = b.toarray()
    b = b[1:, :]  # this is bx and by
    del V, R, C, i, j, net_idx, pad, connected_net, gate_number

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

```

Here, we built only *Global Placement*, which is not *Detail Placement* or *Legalization*, therefore the overlap of the cell position can be occurred .

#### 2.4.3 Forced-Directed Placement

##### 2.4.3.1 Original Algorthm in reference

Forced-Directed Placement is mechanical analogy of a mass-spring stytem, using *Hooke’s-Law* springs. We suppose that each cell gets forces from the connected wires and the final position is that makes the force be zero. 

| The force from one cell to the other cell which are connected each other | The condition for the determined condition                   |      |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ---- |
| <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0leom67dj30i805cq2x.jpg" alt="image-20211203144417560" style="zoom:50%;" /> | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0o5necaxj30c806w749.jpg" alt="image-20211203144436017" style="zoom:50%;" /> |      |

| Diagramed ZFT(Zero Force Target) position                    | The ZFT position formula                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0lgaa36oj30vu0jgwft.jpg" alt="image-20211203144549649" style="zoom:50%;" /> | ![image-20211203144727556](https://tva1.sinaimg.cn/large/008i3skNgy1gx0lhzlktxj311e0bwab0.jpg) |

As original pseudo code of Forced-Directed Placement is below. This is implementated in `forced_direct.py`. The `relocate()` function is not implemented yet, so we can replace code as the above code in `if`  condition.

<img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0lkt61r6j31eu0u07ax.jpg" alt="image-20211203145008106" style="zoom:20%;" />

```python
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
```

##### 2.4.3.2 Suggestion Algorithm 

In this code, the pros and cons exist.

- Pros: The position of each cell is determined at once, so the speed is fast. The number of operations is linearly proportional to n when the number of cells is n.
- Cons: Countermeasures against overlapping locations have not been resolved yet. In addition, since ZFT is calculated only once based on random cells, mechanical analysis was not completely performed.

As the solution of overlapping position, there's some methods for that line *Chain Move* or *Ripple Move*, But this document suggest the another method; repulsive force. Here, we suppose that there's another type of force, like magnetic repulsive force. However, using this formula, we can't get the solution position linearly at once. Therefore, this project implemented the particle simulation, which considers the particle kinetic moves.

```python
def move(net_list, gate_list, pad_list):
    unit_time = 0.5
    for i in range(len(gate_list)):
        gate_i: Gate = gate_list[i]
        # velocity update
        gate_i.velocity = gate_i.velocity + (gate_i.force / gate_i.mass) * unit_time
        # position update
        gate_i.coordinate = gate_i.coordinate + gate_i.velocity * unit_time
```

Here, we should the force updates of each objects. The force update function is also in `forced_directed.py`. In this function, the force considers not only hook's forces but also repulsive force.

```python
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
        gate_i.force = force

```

However, there's a mistake in this modeling, because the stability convergence is not come true. This [gif](https://imgur.com/93MqdOK)  is the simulation result of above modeling. The name of this benchmark is `struct`.

![Animation](https://imgur.com/93MqdOK)

Due to above situation, this project add the *Friction* in the force. The friction should proportional to the velocity of particle.

```python
def get_forces(net_list, gate_list, pad_list):
...

  # force update
  gate_i.force = force - 20 * gate_i.velocity  # consider the friction

...
```

Now, the convergence of the simulation can be occured like [this](https://imgur.com/a/SdUuGkM).

![Animation2](https://imgur.com/a/SdUuGkM)



| Initial state                                                | Final state                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![initial](Report.assets/008i3skNgy1gx0o61gwcbj30rs0rs1ae.jpg) | ![0999](https://tva1.sinaimg.cn/large/008i3skNgy1gx0o6j9kzpj30rs0rstnq.jpg) |

## 3. Conclusion

### 3.1 Simulated Annealing

SA takes a lot of running times, but the implementation is simple and it doesn't occur the overlap position, which menas the detail placement is not required respectively.

|        | Initial Placement                 | Final Placement                   | Initial HPWL | Final HPWL |
| ------ | --------------------------------- | --------------------------------- | ------------ | ---------- |
| struct | ![00001](Report.assets/00001.png) | ![29675](Report.assets/29675.png) | 170566       | 82640      |

![HPWL](Report.assets/HPWL-8521177.png)



![Animation](Report.assets/MQdfymq)

### 3.2 Quadratic Placement

This Placement had a very short running time similar to 3.3.1, but Detail Placement and Legalization seemed necessary. The following are visualizations for each benchmark, initial HPWL, final HPWL, and delta HPWL.

|      | visualization                                                | initial HPWL (randomized placement) | final HPWL        | delta HPWL         |
| ---- | ------------------------------------------------------------ | ----------------------------------- | ----------------- | ------------------ |
| toy1 | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0oym6itvj30rs0rsjsu.jpg" alt="toy1" style="zoom:33%;" /> | 1926.7                              | 549.8224186929145 | 1376.8775813070856 |



|      | visualization                                                | initial HPWL (randomized placement) | final HPWL        | delta HPWL         |
| ---- | ------------------------------------------------------------ | ----------------------------------- | ----------------- | ------------------ |
| toy2 | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0p1olh8pj30rs0rsju0.jpg" alt="toy2" style="zoom:33%;" /> | 3509.6999999999994                  | 1056.597161752309 | 2453.1028382476907 |







|          | visualization                                                | initial HPWL (randomized placement) | final HPWL         | delta HPWL        |
| -------- | ------------------------------------------------------------ | ----------------------------------- | ------------------ | ----------------- |
| primary1 | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0p2dk3x2j30rs0rsane.jpg" alt="toy2" style="zoom:33%;" /> | 83765.30000000008                   | 10800.330897805667 | 72964.96910219442 |



|       | visualization                                                | initial HPWL (randomized placement) | final HPWL         | delta HPWL         |
| ----- | ------------------------------------------------------------ | ----------------------------------- | ------------------ | ------------------ |
| fract | <img src="https://tva1.sinaimg.cn/large/008i3skNgy1gx0p3ft68pj30rs0rstd5.jpg" alt="toy2" style="zoom:33%;" /> | 13940.999999999998                  | 2786.5724334828187 | 11154.427566517179 |



|        | visualization                                                | initial HPWL (randomized placement) | final HPWL         | delta HPWL         |
| ------ | ------------------------------------------------------------ | ----------------------------------- | ------------------ | ------------------ |
| struct | <img src="Report.assets/struct.png" alt="struct" style="zoom:33%;" /> | 170423.39999999994                  | 10475.303983154754 | 159948.09601684517 |

|        | visualization                                                | initial HPWL (randomized placement) | final HPWL         | delta HPWL       |
| ------ | ------------------------------------------------------------ | ----------------------------------- | ------------------ | ---------------- |
| biomed | <img src="Report.assets/biomed.png" alt="biomed" style="zoom:33%;" /> | 477026.8999999998                   | 17380.689419776783 | 459646.210580223 |



### 3.3 Forced-Directed Placement



The trial benchmark will only be `struct`.

#### 3.3.1 Original Placement

|        | Initial placement                             | Final placement                       | Initial HPWL | Final HPWL | Delta HPWL |
| ------ | --------------------------------------------- | ------------------------------------- | ------------ | ---------- | ---------- |
| struct | ![initial](Report.assets/initial-8519168.png) | ![initial](Report.assets/initial.png) | 173943       | 60709      | 113234     |



#### 3.3.2 Suggestion Algorithm



|        | Initial placement                             | Final placement                   | Initial HPWL | Final HPWL | Delta HPWL |
| ------ | --------------------------------------------- | --------------------------------- | ------------ | ---------- | ---------- |
| struct | ![initial](Report.assets/initial-8519389.png) | ![final](Report.assets/final.png) | 168735       | 17551      | 156392     |

#### 3.3.3 Comparision

|        | Original Algorithm                    | Suggestion Algorithm              | HPWL(Original Algorithm) | HPWL(Suggestion Algorithm) |
| ------ | ------------------------------------- | --------------------------------- | ------------------------ | -------------------------- |
| struct | ![initial](Report.assets/initial.png) | ![final](Report.assets/final.png) | 60709                    | 17551                      |

As mentioned above, the existing algorithm calculates the ZFT only once at an initial random position, so it ends in a state where the force balance of all cells is not properly achieved. However, in the presented method, it can be seen that the proposed algorithm with the value of HPWL is much better because it ends after the force balance of all cells is achieved.

In the presented algorithm, it can be seen that each cell is a little farther away from each other because the repulsive force is applied so that the overlap does not occur even if all cells are balanced. This repulsive force can be adjusted by adjusting the coefficient of restitution to achieve the desired spacing between cells.

### 3.3.4 Summary

SA does not require detail placement, but has a running time of 100 to 10000 times more than other placements, and requires a lot of computer resources. The Final Objective function value is also inconsistent compared to other methods.

Quadratic placement has a very fast speed than Forced-directed placement, but there was quite a high cell density and a lot of overlap, and it is expected to have a Final Objective function value similar to SA after detail placement.

Forced Directed placement has a complexity of O(n^2), so it is a little slower than Quadratic placement, but it is significantly faster than SA and has a decent Final Objective function value.
