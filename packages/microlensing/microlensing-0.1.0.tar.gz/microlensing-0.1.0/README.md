# Introduction
This repository contains source code for 

1. generating microlensing magnification maps,
2. locating microlensing critical curves and caustics, and
3. determining the number of microlensing caustic crossings,

all on GPUs.

## Methods
We utilize Inverse Polygon Mapping (IPM, Mediavilla et al. [2006](https://ui.adsabs.harvard.edu/abs/2006ApJ...653..942M/abstract), [2011](https://ui.adsabs.harvard.edu/abs/2011ApJ...741...42M/abstract)), combined with the Fast Multipole Method (FMM, Greengard and Rokhlin [1987](https://ui.adsabs.harvard.edu/abs/1987JCoPh..73..325G/abstract)) as suggested and used by Jiménez-Vicente and Mediavilla ([2022](https://ui.adsabs.harvard.edu/abs/2022ApJ...941...80J/abstract)) for CPUs, in order to generate magnification maps. Calculations for allocating the areas of the IPM cells among the pixels to which they map use the Sutherland-Hodgman ([1974](https://doi.org/10.1145/360767.360802)) algorithm.

We utilize Witt's ([1990](https://ui.adsabs.harvard.edu/abs/1990A&A...236..311W)) method to locate the microlensing critical curves and caustics, while taking advantage of the FMM again to decrease computation time for terms involving derivatives of the microlensing potential. In order to locate the roots of the parametric critical curve equation, we employ the [Aberth](https://doi.org/10.2307/2005621)-[Ehrlich](https://doi.org/10.1145/363067.363115) method, a cubically convergent algorithm that allows for simultaneous approximations of the roots of a polynomial. 

We use the fact that the caustics are clockwise (under the chosen critical curve parametrization) oriented closed curves to utilize the winding number in order to calculate a two dimensional map of the the number of caustic crossings (Wambsganss et al. [1992](https://ui.adsabs.harvard.edu/abs/1992A&A...258..591), Granot et al. [2003](https://ui.adsabs.harvard.edu/abs/2003ApJ...583..575G)). We use Sunday's ([2001](https://web.archive.org/web/20130126163405/http://geomalgorithms.com/a03-_inclusion.html)) algorithm to calculate the winding number of the discretized caustic polygons around the center of every pixel, efficiently creating a map that provides the number of caustic crossings.

## Credits
You are free to use this code under the provided license. A paper (or two) will appear at some point in the near future; if you use the code, appropriate citation(s) would be appreciated when/where necessary. Suggested improvements and bugfixes are also always appreciated! 

I make no promise that the current state of the code will stay the same, or that things will always be backwards compatible. Poor design choices I made in the past may need be changed to make the future better!

I would love to be considered for involvement in any projects which make use of these tools, as I'd like to think I bring a bit of microlensing knowledge to the table :). I can be reached at [weisluke@alum.mit.edu](mailto:weisluke@alum.mit.edu).


## Dependencies
The code is written to be independent of anything besides the C++ standard libraries and the Thrust libraries that come with CUDA. We implement IPM, the FMM, the Sutherland-Hodgman algorithm, the Aberth-Ehrlich method, and Sunday's algorithm ourselves.

The bulk of the code is written using NVIDIA's CUDA, and you will need a CUDA installation to compile and run it. We additionally require a C++20 compliant compiler.

## Repository layout
The `include` directory contains the bulk of the code, which is written mostly as templated objects and functions. The `src` directory contains files for creating executables and libraries (see the [python](#python) section below). The `bin` directory holds compilation output (see the section on [compiling](#compiling)). The `microlensing` directory contains python code for ease of use (see once more the [python](#python) section below), while the root directory contains a couple example python notebooks outlining usage.

## Compiling
Compilation has been tested with the GNU compiler version 12.2.0 and the CUDA HPC SDK version 23.9.

First, clone the repository.
```
git clone https://github.com/weisluke/microlensing.git
```

Then, simply run 
```
source compile
```
to run the compilation file. This should create 5 executables and 4 libraries in the `bin` directory. 

I'll note that this repository contains the 4 libraries precompiled and placed in the `./microlensing/lib/` directory already. These libraries may or may not work on your hardware, as they were compiled for a particular cluster, but you can try running the example [python](#python) notebook first to see if they do. If there are errors, you will need to compile everything yourself.

## python

In addition to command line programs, we also provide wrappers for our code that allow them to be used with python once the relevant libraries are [compiled](#compiling). This eases the need to save output from the executables to disk and then read them from disk; we directly copy from managed memory to a numpy array once magnification maps and other objects are created. 

Instead of cloning this repository, you can `pip install microlensing` 

The file `example.ipynb` contains *very* brief examples of the python packages I've written to create microlensing magnification maps, calculate critical curves and caustics, and calculate number of caustic crossings maps. The file `view_output.ipynb` contains an example of reading output from the IPM executable.

