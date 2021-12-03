import numpy as np
import matplotlib.pyplot as plt
import pygame
import data_structures
import random
import parser
import save_gif

pygame.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
size = [1000, 1000]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

net_colors = []


def set_net_colors(net_list):
    for i in range(len(net_list)):
        # net_iter: data_structures.Net = net_list[i]
        net_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        net_colors.append(net_color)


def print_pads_and_gates(pad_list, gate_list, remark):
    gate_coordinates = np.zeros((len(gate_list), 2), dtype=np.float64)
    for i in range(len(gate_list)):
        gate_coordinates[i, 0] = gate_list[i].coordinate[0]
        gate_coordinates[i, 1] = gate_list[i].coordinate[1]

    pad_coordinates = np.zeros((len(pad_list), 2), dtype=np.float64)
    for i in range(len(pad_list)):
        pad_coordinates[i, 0] = pad_list[i].coordinate[0]
        pad_coordinates[i, 1] = pad_list[i].coordinate[1]

    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.plot(gate_coordinates[:, 0], gate_coordinates[:, 1], 'b^')
    plt.plot(pad_coordinates[:, 0], pad_coordinates[:, 1], 'r^')
    plt.title(remark)
    plt.show()


def pygame_quit(save_image=0, FD=1):
    if save_image:
        if FD:
            save_gif.save_gif()
        pass

    pygame.quit()


def draw_graph_array(ndarray=[], csv_name="", title="HPWL", graph_name="graph.png"):
    if csv_name == "":
        pass
    else:
        ndarray = np.genfromtxt(csv_name)
    ndarray = ndarray[1:]
    length = len(ndarray)
    y = ndarray
    x = np.arange(0, length, 1)
    plt.title(title)
    plt.plot(x, y)
    plt.show()
    plt.savefig(graph_name)


def draw_window(pad_list, gate_list, net_list, remark=0, initial_display=0, animation_save=0, path="", ver="",
                information=[]):
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

        if ver == "visualization":
            filename = "%04d.png" % remark
            pygame.image.save(screen, "Images_visual_basic/" + filename)
        if ver == "SA":
            T = information[0]
            HPWL = information[1]
            myFont = pygame.font.SysFont("arial", 100, True, False)
            T_text = myFont.render("T: " + str(round(T, 2)), True, BLACK)
            HPWL_text = myFont.render("HPWL: " + str(int(HPWL)), True, BLACK)
            screen.blit(T_text, [10, 30])
            screen.blit(HPWL_text, [10, 130])
            filename = "Images_SA/Snaps/%05d.png" % remark
            pygame.image.save(screen, filename)
        elif ver == "FD1":
            pygame.image.save(screen, "FD_images/" + "initial" + ".png")
        elif ver == "FD2":
            pygame.image.save(screen, "FD_images/" + "final" + ".png")

        elif ver == "FD3":
            myFont = pygame.font.SysFont("arial", 100, True, False)
            remark_text = myFont.render("N: " + str(remark), True, BLACK)
            screen.blit(remark_text, [10, 30])
            pygame.image.save(screen, "FD_images/result" + str(remark) + ".png")

            # if initial_display == 1:
            #     pygame.image.save(screen, "FD_images/initial" ".jpeg")
            # else:
            #     pygame.image.save(screen, "FD_images/result" + str(remark) + ".jpeg")
            # pygame.display.flip()
        elif ver == "Q":
            pygame.image.save(screen, "Images_Q/" + information[0] + ".png")
            print(".")
        elif animation_save:
            filename = path + "/Snaps/%04d.png" % remark
            pygame.image.save(screen, filename)
            pygame.display.flip()
        else:
            pygame.display.flip()


def main():
    net_list, gate_list, pad_list = parser.parser("benchmarks/3QP/test3")
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


if __name__ == "__main__":
    main()
    quit()
