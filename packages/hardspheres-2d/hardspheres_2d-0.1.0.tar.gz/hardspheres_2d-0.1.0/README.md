# Hard Spheres in 2d
> Simulating hard spheres in two dimensions using event driven molecular dynamics and visualizing rotational symmetry using psi-6.

![Melting hexagon of hard spheres](./melting-hexagon.gif)

## Setup

    git clone
    cd hardspheres-2d
    uv sync

For the installation of uv see [here](https://docs.astral.sh/uv/getting-started/installation/).

Note: this project uses Rust 1.82. So you may need to [install the rust toolchain](https://www.rust-lang.org/tools/install).

## How to use

### Command Line

To run the event driven molecular dynamics simulation from your command line you can check out

    uv run hardspheres2d --help


### Notebook

Alternatively, the notebook `./melting-hard-sphere-hexagons.ipynb` contains all the steps to set up and run event driven molecular dynamcis on your machine. As well as some sanity checks to better understand what is going on.

To visualize the dynamics you may want to install [ovito](https://www.ovito.org). The base version is sufficient.

## Developing

During your rust edits you want to update your build artefacts so you can use them from python / a notebook. For this please use

    make update
