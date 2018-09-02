# Evolutive Turing Machine

_Because we are meant to create life_

## Introduction

The Synthetic Life initiative aims to support the emergence of a new autonomous and self-improving artificial life form. The Evolutive Turing Machine is the first project implementing a simple and evolving microcosm.

## Concept

![Evolutive Turing Machine screenshot](http://syntheticlife.org/img/screenshot1.png)

[Execution on a live server  here](http://pd.syntheticlife.org)

### Description

The Evolutive Turing Machine program simulates cells living and evolving in a petri dish. Like in the real world, these cells can eat and get energy from the nutritive substrate of the petri dish, use this energy to live, move or divide and can die. These cells are also subject to spontaneous mutation in their genome represented by their turing machine action table. The natural selection process makes the fittest cells survive.

We have chosen the Turing Machine as the core of the cells because it can simulate any computer algorithm. This first implementation is in Python because of its simplicity and the libraries available

### Resources

[Wikipedia Petri dish](http://en.wikipedia.org/wiki/Petri_dish)

[Wikipedia Cell](http://en.wikipedia.org/wiki/Cell_%28biology%29)

[Wikipedia Turing Machine](http://en.wikipedia.org/wiki/Turing_machine)

[Wikipedia Genetic Algorithm](http://en.wikipedia.org/wiki/Genetic_algorithm)

[Wikipedia Natural Selection](https://en.wikipedia.org/wiki/Natural_selection)

### Contact

If you want to know more about the project or get involved feel free to email us at [github@syntheticlife.org](mailto:github@syntheticlife.org)

## Installation

### Dependencies

* Numpy
* TkInter
* Pillow

`apt-get install python python-numpy python-tk python-imaging python-imaging-tk`

## Execution

### Command line

* On desktop, `python syntheticlife.py`, `./syntheticlife.py` or `gui_start` to run the program and display the petri dish evolution in a window

* On server, `server_start` and `server_stop` to run the program in background

### Arguments

* `-h`, `--help` To show the help documentation and arguments description

* `--nogui` Run the program without displaying the petri dish

* `--file data.bin` Load and save the petri dish in this file

* `--duration N` The duration in seconds between two backups. No backup by default.

* `--image image.png` The image of the petri dish updated after every loop. No image saved by default.
