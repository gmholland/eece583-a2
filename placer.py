import random
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

def open_benchmark(*args):
    pass


def place(*args):
    pass


# main function
if __name__ == '__main__':

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
