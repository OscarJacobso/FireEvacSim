import numpy as np
from celluloid import Camera
import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


def set_elements_rec(mesh, row, col):

    def filter_func(el, mesh = mesh):

        if (el[0] < 1 or el[1] < 1 or el[0] > mesh.shape[0] - 2 or el[1] > mesh.shape[1] - 2):

            return False

        if (mesh[el[0],el[1]] == 1 or mesh[el[0],el[1]] == 500):

            return False

        return True


    diag_ind = [(row - 1, col - 1), (row - 1, col + 1), (row + 1, col - 1), (row + 1, col + 1)]
    hor_ind = [(row - 1, col), (row, col + 1), (row, col - 1), (row + 1, col)]
    diag_ind = list(filter(filter_func, diag_ind))
    hor_ind = list(filter(filter_func, hor_ind))
    neighbor_ind = diag_ind + hor_ind
    set_elements(mesh, row, col, diag_ind, lamb = 1.5)
    set_elements(mesh, row, col, hor_ind, lamb = 1)



    while True:

        new_neighbours = []
        mesh_old = mesh.copy()
        for temprow, tempcol in neighbor_ind:

            diag_ind = [(temprow - 1, tempcol - 1), (temprow - 1, tempcol + 1), (temprow + 1, tempcol - 1), (temprow + 1, tempcol + 1)]
            hor_ind = [(temprow - 1, tempcol), (temprow, tempcol + 1), (temprow, tempcol - 1), (temprow + 1, tempcol)]

            try:
                diag_ind = list(filter(filter_func, diag_ind))
                hor_ind = list(filter(filter_func, hor_ind))
            except:
                raise ValueError(f"{(temprow, tempcol)}")
            templs = diag_ind + hor_ind
            set_elements(mesh, temprow, tempcol, diag_ind, lamb = 1.5)
            set_elements(mesh, temprow, tempcol, hor_ind, lamb = 1)

            for tempind in templs:
                if tempind not in neighbor_ind and tempind not in new_neighbours:
                    new_neighbours.append(tempind)

        bool_matr = (mesh_old == mesh)
        bool_matr = bool_matr.flatten()
        if all(bool_matr):
            break

        neighbor_ind = new_neighbours


def set_elements(mesh, row, col, indicies, lamb = 1):

    for ind in indicies:

        if mesh[ind[0],ind[1]] == 500:
            continue
        elif mesh[ind[0],ind[1]] !=0:
            mesh[ind[0],ind[1]] = min([mesh[ind[0],ind[1]], mesh[row,col] + lamb])
        else:

            mesh[ind[0],ind[1]] = mesh[row,col] + lamb

def draw_mesh_art(rows,cols, door_pos, lamb):
    mesh = 500 * np.ones(((rows + 2), cols + 2))
    mesh[1:rows + 1, 1:cols + 1] = 0

    for i in range(4, 16 + 4, 4):

        mesh[4:12,i] = 500

    for door in door_pos:
        mesh[door[0], door[1]] = 1

    for ax in range(4):

        doorposition_vec = np.where(mesh[:,0] == 1)[0]
        if len(doorposition_vec) != 0:

            for door in doorposition_vec:

                if mesh[door,1] != 0:

                    mesh[door, 1] = min([mesh[door, 1], mesh[door, 0] + 1])
                else:
                    mesh[door, 1] = mesh[door, 0] + 1

                if mesh[door + 1, 1] != 0:

                    mesh[door + 1, 1] = min([mesh[door + 1, 1], mesh[door, 0] + lamb])
                else:
                    mesh[door + 1, 1] = mesh[door, 0] + lamb

                if mesh[door - 1, 1] != 0:

                    mesh[door - 1, 1] = min([mesh[door - 1, 1], mesh[door, 0] + lamb])
                else:
                    mesh[door - 1, 1] = mesh[door, 0] + lamb



                set_elements_rec(mesh, door, 1)


        mesh = np.rot90(mesh)

    return mesh


def request_move(neigbourhood, people, indicies, curr_pos):

    temp_neigbourhood = neigbourhood.copy()
    temppeople = people.copy()

    possible_moves = []
    floor_val = []

    for i, row in enumerate(temppeople):
        for j, col in enumerate(row):
            if col == 0 or indicies[i][j] == curr_pos:
                possible_moves.append(indicies[i][j])
                floor_val.append(temp_neigbourhood[i, j])

    comb_list = [[dist, ind] for dist, ind in sorted(zip(floor_val, possible_moves))]
    min_val = [comb_list[0]]

    for i in range(1, len(comb_list)):
        if min_val[0][0] == comb_list[i][0]:
            min_val.append(comb_list[i])
        else:
            break


    if len(min_val) > 1:

        ind = np.random.choice(list(range(len(min_val))))

        return (min_val[ind][1][0], min_val[ind][1][1])

    else:

        return (min_val[0][1][0],min_val[0][1][1])

def panic(prob):
    return np.random.choice([0,1], size = 1, p = [1 - prob, prob])


def handle_requests(people_new, requests):

    requests = sorted(requests, key = lambda x: x[1])

    ind = 0
    nr_requests = len(requests)


    while ind < nr_requests:
        temp_req_lst = [requests[ind]]
        ind += 1


        while ind < nr_requests and requests[ind][1] == temp_req_lst[0][1]:
            temp_req_lst.append(requests[ind])

            ind += 1



        temp_num_req = len(temp_req_lst)
        if temp_num_req > 1:

            rand_ind = np.random.choice(list(range(temp_num_req)))

            lucky_man = temp_req_lst.pop(rand_ind)

            people_new[lucky_man[1][0], lucky_man[1][1]] = 1
            people_new[lucky_man[0][0], lucky_man[0][1]] = 0


            for unlucky_man in temp_req_lst:

                people_new[unlucky_man[0][0], unlucky_man[0][1]] = 1

        else:
            people_new[temp_req_lst[0][1][0], temp_req_lst[0][1][1]] = 1
            if temp_req_lst[0][0] != temp_req_lst[0][1]:
                people_new[temp_req_lst[0][0][0], temp_req_lst[0][0][1]] = 0

    return people_new



def step(mesh, people, panic_prob, door_pos):

    requests = []
    dims = people.shape
    for door in door_pos:
        people[door[0], door[1]] = 0

    for i in range(1, dims[0] - 1):
        for j in range(1, dims[1] - 1):

            if people[i, j] == 0 or people[i, j] == 500:
                continue

            if panic(panic_prob):
                requests.append([(i,j), (i,j)])

            else:
                indicies = [[[x,y] for y in range(j-1 , j + 2)] for x in range(i-1, i + 2)]

                move_request = request_move(mesh[i-1:i+2,j-1:j+2], people[i-1:i+2,j-1:j+2], indicies, [i,j])
                requests.append([(i,j), move_request])


    return handle_requests(people, requests)


def run_sim(mesh_dim, panic_prob, time_steps, door_pos,lamb, gen_gif = False, filename = None):
    np.random.seed()

    floor_mesh = draw_mesh_art(mesh_dim[0],mesh_dim[1], door_pos, lamb)
    people_mesh = 500 * np.ones((mesh_dim[0] + 2,mesh_dim[1] + 2), dtype = int)
    people_mesh[1:mesh_dim[0] + 1, 1:mesh_dim[1] + 1] = 0

    for i in range(4, 16 + 4, 4):

        people_mesh[4:12,i] = 500

    people_mesh[people_mesh == 0] = np.random.choice([0,1], size = people_mesh[people_mesh == 0].shape, p = [0.60,0.40])


    for door in door_pos:
        people_mesh[door[0], door[1]] = 0

    T = time_steps
    t = 0
    if gen_gif:
        fig = plt.figure()
        camera = Camera(fig)
        plot_mesh(people_mesh, fig)
        camera.snap()

    while t < T:

        people_mesh = step(floor_mesh, people_mesh, panic_prob, door_pos)
        t += 1
        if gen_gif:
            plot_mesh(people_mesh, fig)
            camera.snap()

        if len(people_mesh[people_mesh == 1]) == 0:
            break

    if gen_gif:
        gifs_dir = os.path.join(MAIN_DIR, 'gifs')
        os.makedirs(gifs_dir, exist_ok=True)
        animation = camera.animate()
        animation.save(os.path.join(gifs_dir, filename))

    return t


def plot_mesh(mesh, fig):
    color_dict = {0: np.array([255, 255, 255]), 1: np.array([255, 0, 0]), 500: np.array([0, 0, 0])}
    res = [[color_dict[int(col)] for col in row] for row in mesh]
    res = np.array(res)

    if not fig:
        plt.figure()

    plt.imshow(res)

    if not fig:
        plt.show()




if __name__ == "__main__":

    tot_doors = []

    for i in range(14, 0, -1):
        tot_doors.append([[i, 0]])
    for i in range(1,19):
        tot_doors.append([[0, i]])

    for i in range(1,15):
        tot_doors.append([[i, 19]])

    for i in range(18,0, -1):
        tot_doors.append([[15, i]])



    panic_prob_vec = [0.05]
    num_rep = 10
    filename = 'example_furnished_8_0.gif'
    evac_time_vec = []
    run_sim((14,18), panic_prob_vec[0], 300, [[8,0]], 1.5, gen_gif = True, filename = filename)

    loop = 0 # Set to 1 to run the full simulation loop, 0 to just generate a single gif.
    if loop:
        for doors in tot_doors:
            tempvec = []
            for i in range(num_rep):
                evacuation_time = run_sim((14,18), panic_prob_vec[0], 2000, doors, 1.5)
                tempvec.append(evacuation_time)
            evac_time_vec.append(np.mean(tempvec))

    dor = np.array(list(range(len(evac_time_vec)))) + 1

    plt.figure()
    plt.plot(dor, evac_time_vec)
    plt.xlabel('Door position')
    plt.ylabel('Average evacuation time in ticks')
    plt.grid(True)
    plt.show()
