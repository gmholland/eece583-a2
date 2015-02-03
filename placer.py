import os.path
import random
import logging
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class Cell:
    """Class representing a cell site."""

    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
        self.content = 'empty'

    def is_empty(self):
        if self.content == 'empty':
            return True
        else:
            return False


class Layout:
    """Class representing the chip layout."""

    def __init__(self):
        self.ncells = 0
        self.nconnections = 0
        self.nrows = 0
        self.ncols = 0
        self.grid = [[]]

    def init_grid(self, nrows, ncols):
        """Initialize the grid to given size by populating with empty Cells."""
        self.grid = [[Cell(col=x, row=y) for x in range(ncols)] for y in range(nrows)]
        self.nrows = nrows
        self.ncols = ncols


def parse_netlist(filepath):
    """Parse a netlist and populate the layout.grid.
    
    filepath - the full path of the netlist file to parse"""
    with open(filepath, 'r') as f:
        # first line is grid size
        line = f.readline().strip().split()
        layout.ncells = int(line[0])
        layout.nconnections = int(line[1])
        nrows = int(line[2])
        ncols = int(line[3])
        layout.init_grid(nrows, ncols)

        logging.info('ncells={}, nconnections={}, nrows={}, ncols={}'.format(
            layout.ncells, layout.nconnections, nrows, ncols))


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
    parse_netlist(openfilename)

    # enable the Place button
    place_btn.state(['!disabled'])


def place(*args):
    pass


# main function
if __name__ == '__main__':
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
