import os.path
import random
import logging
from math import exp
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class Node:
    """Class representing a circuit element.
    
    Data attributes:
        loc - Site of temporary location of cell
        nets - list of nets the node belongs to"""

    def __init__(self):
        self.loc = None
        self.nets = []

    def get_partial_cost(self):
        """Get HPBB cost for nets that include this node."""
        partial_cost = 0
        for net in self.nets:
            partial_cost += net.get_hpbb()
        return partial_cost


class Net:
    """Class representing a net.
    
    Data attributes:
        nodes - list of nodes the net connects"""

    def __init__(self, nodes=[]):
        self.nodes = nodes

    def get_hpbb(self):
        """Get length of half-perimter bounding box of net."""
        if not self.nodes:
            return 0

        # initialize max and mins to first element coords
        x_min = x_max = self.nodes[0].loc.col
        y_min = y_max = self.nodes[0].loc.row

        # find max and min coordinates
        for node in self.nodes[1:]:
            if node.loc.col < x_min:
                x_min = node.loc.col
            elif node.loc.col > x_max:
                x_max = node.loc.col

            if node.loc.row < y_min:
                y_min = node.loc.row
            elif node.loc.row > y_max:
                y_max = node.loc.row

        # calculate half perimeter bounding box
        # - multiply y coord by 2 to account for empty rows between cells
        hpbb = (x_max - x_min) + 2*(y_max - y_min)
        return hpbb


class Site:
    """Class representing a cell site."""

    def __init__(self, row=None, col=None):
        self.row = row
        self.col = col
        self.content = None

    def is_empty(self):
        return self.content is None


class Layout:
    """Class representing the chip layout."""

    def __init__(self):
        self.ncells = 0
        self.nconnections = 0
        self.nrows = 0
        self.ncols = 0
        self.nsites = 0
        self.grid = [[]]
        self.netlist = []
        self.nodelist = []

    def init_grid(self, nrows, ncols):
        """Initialize the grid to given size by populating with empty sites."""
        self.grid = [[Site(col=x, row=y) for x in range(ncols)] for y in range(nrows)]
        self.nrows = nrows
        self.ncols = ncols
        self.nsites = nrows * ncols

    def init_nodelist(self, ncells):
        """Initialize the node list by populating with ncells Nodes."""
        self.nodelist = [Node() for i in range(self.ncells)]

    def get_site_by_id(self, site_id):
        """Return site from grid given a site ID."""
        row = site_id // self.ncols
        col = site_id % self.ncols
        return self.grid[row][col]

    def get_cost(self):
        """Caclulate cost of current placement."""
        cost = 0
        for net in self.netlist:
            cost = cost + net.get_hpbb()
        return cost

    def parse_netlist(self, filepath):
        """Parse a netlist and populate the grid.
        
        filepath - the full path of the netlist file to parse"""
        with open(filepath, 'r') as f:
            # first line is ncells, nconnections and grid size
            line = f.readline().strip().split()

            # initialize node list
            self.ncells = int(line[0])
            self.init_nodelist(self.ncells)

            self.nconnections = int(line[1])

            # initialize grid of sites
            nrows = int(line[2])
            ncols = int(line[3])
            self.init_grid(nrows, ncols)

            logging.info('ncells={}, nconnections={}, nrows={}, ncols={}, nsites={}'.format(
                self.ncells, self.nconnections, nrows, ncols, self.nsites))

            # next lines describe netlist
            while True:
                line = f.readline().strip().split()

                # stop once end of file is reached
                if not line:
                    break

                # each line corresponds to a net giving node IDs of the nodes
                #  contained in the net
                ncells_in_net = line[0]
                net = Net()
                for i in line[1:]:
                    node_id = int(i)
                    # lookup corresonding node in nodelist
                    node = self.nodelist[node_id]

                    node.nets.append(net)
                    net.nodes.append(node)

                self.netlist.append(net)

        logging.info('parsed {} nets in netlist file'.format(
            len(self.netlist)))


def open_benchmark(*args):
    """Function called when pressing Open button.
    
    Opens a dialog for user to select a netlist file and calls
    parse_netlist."""

    # open a select file dialog for user to choose a benchmark file
    openfilename = filedialog.askopenfilename()
    # return if user cancels out of dialog
    if not openfilename:
        return

    logging.info("opened benchmark:{}".format(openfilename))
    filename.set(os.path.basename(openfilename))
    layout.parse_netlist(openfilename)

    # enable the Place button
    place_btn.state(['!disabled'])


def initialize_placement():
    """Randomly assign each node in the nodelist to a cell site."""

    # select ncells random site IDs
    rand_site_ids = random.sample(range(layout.nsites), layout.ncells)

    for i, rand_site_id in enumerate(rand_site_ids):
        # assign selected site to next node in nodelist
        site = layout.get_site_by_id(rand_site_id)
        node = layout.nodelist[i]
        site.content = node
        node.loc = site


def anneal_inner(temp, niterations):
    """Inner loop of simulated annealing algorithm."""

    for i in range(niterations):
        # randomly select two sites
        [site1, site2] = select_sites()

        # calculate cost of move - only need to consider nets that
        # contain the nodes we swapped
        pre_swap_cost = 0
        if not site1.is_empty():
            node1 = site1.content
            pre_swap_cost += node1.get_partial_cost()
        if not site2.is_empty():
            node2 = site2.content
            pre_swap_cost += node2.get_partial_cost()

        swap_sites(site1, site2)

        post_swap_cost = 0
        if not site1.is_empty():
            node1 = site1.content
            post_swap_cost += node1.get_partial_cost()
        if not site2.is_empty():
            node2 = site2.content
            post_swap_cost += node2.get_partial_cost()

        delta_c = post_swap_cost - pre_swap_cost 

        # r = random(0, 1)
        r = random.random()

        if r < exp(-delta_c / temp):
            # take move (keep swap)
            pass
        else:
            # don't take move (undo swap)
            swap_sites(site2, site1)


def select_sites():
    """Return a list of 2 randomly selected sites, only one may be empty."""
    while True:
        [site_id1, site_id2] = random.sample(range(layout.nsites), 2)
        site1 = layout.get_site_by_id(site_id1)
        site2 = layout.get_site_by_id(site_id2)
    
        # try again if both sites are empty
        if site1.is_empty() and site2.is_empty():
            continue
        else:
            break

    return [site1, site2]


def swap_sites(site1, site2):
    """Swap content of two sites."""
    temp_content = site1.content
    site1.content = site2.content
    site2.content = temp_content
    if not site1.is_empty():
        site1.loc = site1
    if not site2.is_empty():
        site2.loc = site2


def get_new_temp(temp, beta):
    """Return the next annealing temperature."""
    return beta * temp


def exit_condition(temp):
    """Check annealing exit condition."""
    return True


def place(*args):
    """Place the circuit using simulated annealing."""

    T = 1 # starting temperature
    k = 10 # constant for num iterations at each temp
    beta = 0.9 # factor for reducing temp

    # first place all nodes randomly
    initialize_placement()

    # set start temperature
    temp = T
    #niterations = int(k * (layout.ncells)**(4/3))
    niterations = int(layout.ncells**(4/3))
    prev_cost = layout.get_cost()

    while True:
        anneal_inner(temp, niterations)

        # reduce temp
        temp = get_new_temp(temp, beta)

        if exit_condition(temp):
            break


# main function
if __name__ == '__main__':
    # set random number generator seed 
    # TODO make configurable via GUI or cmd line
    random.seed(0)

    # setup logfile
    logging.basicConfig(filename='placer.log', filemode='w', level=logging.INFO)

    # chip layout
    layout = Layout()

    # setup gui
    root = Tk()
    root.title("Assignment2-Placement")

    # add frames to gui
    top_frame = ttk.Frame(root, padding="3 3 12 12")
    top_frame.grid(column=0, row=0)
    top_frame.columnconfigure(0, weight=1)
    top_frame.rowconfigure(0, weight=1)
    canvas_frame = ttk.Frame(top_frame)
    canvas_frame.grid(column=0, row=0, sticky=(N,E,S,W))
    btn_frame = ttk.Frame(top_frame)
    btn_frame.grid(column=0, row=1)

    # setup canvas frame (contains benchmark label and canvas)
    filename = StringVar()
    benchmark_lbl = ttk.Label(canvas_frame, textvariable=filename)
    benchmark_lbl.grid(column=0, row=0)
    canvas = Canvas(canvas_frame, width=640, height=480, bg="dark grey")
    canvas.grid(column=0, row=1, padx=5, pady=5)

    # setup button frame (contains buttons)
    open_btn = ttk.Button(btn_frame, text="Open", command=open_benchmark)
    open_btn.grid(column=0, row=0, padx=5, pady=5)
    place_btn = ttk.Button(btn_frame, text="Place", command=place)
    place_btn.grid(column=1, row=0, padx=5, pady=5)
    place_btn.state(['disabled'])

    # run main event loop for gui
    root.mainloop()
