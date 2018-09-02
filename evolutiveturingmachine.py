#!/usr/bin/python

from petridish import PetriDish
from PIL import Image, ImageTk
import Tkinter as tk
from Tkinter import Tk, Canvas
import config
import random
import time, thread, threading
import numpy as np
import config
import pickle
import argparse
from threading import Thread
import signal
import sys
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

def petriDishToImage(pd, image_resize = 1):

    image = Image.new("RGB", (pd.width, pd.height), "black")
    pixels = image.load()

    # Draw food level
    for x in range(pd.width):
        for y in range(pd.height):
            food_level = int(pd.food_map[x][y] * 255.0 / config.FOOD_LEVEL_VALUE_MAX)
            pixels[x,y] = (255 - food_level, 255 , 255 - food_level)

    # Draw the cells energy level
    for (x, y, direction, cell) in pd.cells + pd.new_cells:
        energy_level = int(cell.energy_level * 255.0 / config.ENERGY_LEVEL_VALUE_MAX)
        pixels[x,y] = (energy_level, 0, 0)

    image = image.resize((image.width * image_resize, image.height * image_resize), Image.NEAREST)

    return image

def save(pd, filename):

    pickle.dump( pd, open( filename, "wb" ) )
    return

def load(filename):

    try:
        pd = pickle.load( open( filename, "rb" ) )
        return pd
    except IOError:
        return PetriDish()


pd = None
image_photo = None
canvas = None
image_on_canvas = None
master = None
start_time = None
end_time = None
stop = False

def updateModel():
    global pd, stop, master, image, args

    logging.info("Start execution")
    start_time = time.time()
    while stop == False:

        logging.info("Generation #{} ({} cells, {} divisions, {} matings, {} mutations)".format(pd.generation, len(pd.cells), pd.nb_of_divisions, pd.nb_of_matings, pd.nb_of_mutations))
        pd.loop()
        #print "Total food and energy:", pd.getTotalFoodAndEnergy() # To check if the simulation the energy conservation principle

        # Save the petri dish at regular time interval
        current_time = time.time()
        elapsed_time = current_time - start_time
        if args.duration > 0 and elapsed_time >= args.duration:
            logging.info("Saving petri dish...")
            save(pd, args.file)
            start_time = time.time()

        # Create and save the image from petri dish
        image = petriDishToImage(pd, config.IMAGE_RESIZE)
        if args.image != None:
            image.save(args.image)

    logging.info("Saving petri dish...")
    save(pd, args.file)

    logging.info("End :)")

    return

def updateView():
    global pd, image, photo, canvas, image_on_canvas, master, args

    photo = ImageTk.PhotoImage(image)
    canvas.itemconfig(image_on_canvas, image = photo)

    master.after(1000 / config.FRAME_RATE, updateView)

    return

def stopModel():
    global stop

    logging.info("Stop! Waiting the end of the loop..")
    stop = True

def onDeleteWindow():
    master.destroy()
    stopModel()

def signalHandler(signal, frame):
    stopModel()

def main():
    global pd, image, photo, canvas, image_on_canvas, master, args

    logging.info("Loading petri dish...")
    pd = load(args.file)

    # Start the petri dish execution thread
    t = Thread(target=updateModel, args=())
    t.start()

    if(args.nogui == True):

        signal.signal(signal.SIGINT, signalHandler)
        signal.pause()

    else:

        image = petriDishToImage(pd, config.IMAGE_RESIZE) # Generate the first image to get the size

        master = Tk()
        canvas = Canvas(master, width=image.width, height=image.height)
        canvas.pack()

        photo = ImageTk.PhotoImage(image)
        image_on_canvas = canvas.create_image(0, 0, image=photo, anchor=tk.NW)

        updateView()

        master.protocol("WM_DELETE_WINDOW", onDeleteWindow)
        master.mainloop()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Evolutive Turing Machine')
    parser.add_argument('--nogui', help='Start without a GUI (for servers)', action='store_true')
    parser.add_argument('--file', default='data.bin', help='The file where to load and save the petri dish', type=str)
    parser.add_argument('--image', default=None, help='The image where to export the petri dish', type=str)
    parser.add_argument('--duration', default='0', help='The time in seconds between two petri dish backup', type=int)
    args = parser.parse_args()
    #print args

    main()
