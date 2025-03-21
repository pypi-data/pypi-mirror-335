import numpy as np


def place_spheres_hexagonal(a: float, r: float, gap: float = 0.0):
    """
    Places hard spheres of radius r in a square of edge length a,
    forming a hexagonal lattice.

    Args:
        a (float): Edge length of the square.
        r (float): Radius of the spheres.

    Returns:
        numpy.ndarray: A 2D numpy array containing the (x, y) coordinates of the sphere centers.
                       Returns an empty array if no spheres can be placed.
    """

    # Calculate the effective edge length, accounting for the boundary condition
    effective_a = a - 2 * r

    # Calculate the lattice constant (distance between sphere centers)
    lattice_constant = 2 * r

    # Calculate the number of spheres that can fit in each direction
    num_x = int(effective_a / lattice_constant)
    num_y = int(effective_a / (np.sqrt(3) * r))

    # Initialize an empty list to store the sphere centers
    centers = []

    # Place the spheres in a hexagonal lattice
    for i in range(num_x):
        for j in range(num_y):
            x = i * (lattice_constant + gap)
            y = j * (np.sqrt(3) * (r + gap))

            # Offset every other row to create the hexagonal pattern
            if j % 2 == 1:
                x += r

            # Check if the sphere is within the square bounds
            if 0 <= x <= effective_a and 0 <= y <= effective_a:
                centers.append([x, y])

    offset = r * 1.1
    return np.array(centers) + offset


def plot_spheres(a: float, r: float, sphere_centers: np.ndarray, save: bool = False):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.set_xlim(0, a)
    ax.set_ylim(0, a)
    ax.set_aspect("equal")  # Ensure the plot is square

    for center in sphere_centers:
        circle = plt.Circle(center, r, color="blue", alpha=0.5)  # type: ignore
        ax.add_patch(circle)

    plt.title(f"Hexagonal Lattice of Spheres (a={a}, r={r})")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()

    if save:
        plt.savefig("hardspheres-hexagon.png")
