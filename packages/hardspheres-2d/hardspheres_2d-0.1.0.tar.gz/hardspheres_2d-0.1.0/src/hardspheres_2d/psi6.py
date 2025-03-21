from dataclasses import dataclass

import numpy as np

from hardspheres_2d import HardSpheres


@dataclass
class DistanceInformation:
    distance_vectors: np.ndarray  # (N,N,d) float tensor with differences
    distances: np.ndarray  # (N,N) float tensor of distances
    neighbor_mask: np.ndarray | None = None  # (N,N) boolean tensor indicating neighbors

    @property
    def has_mask(self) -> bool:
        return self.neighbor_mask is not None


def calc_distance_information(
    s: HardSpheres, radius_multiple: float | None = None
) -> DistanceInformation:
    # Calculate pairwise distances using numpy
    distance_vectors = s.x[:, np.newaxis, :] - s.x[np.newaxis, :, :]
    # distances = np.sqrt(
    #     np.sum(distance_vectors ** 2, axis=2)
    # )
    distances = np.linalg.norm(distance_vectors, ord=2, axis=2)

    # Find neighbors within the specified radius
    if radius_multiple:
        neighbor_mask = distances <= s.sigma * radius_multiple
        np.fill_diagonal(neighbor_mask, False)  # Exclude self-neighbors
    else:
        neighbor_mask = None

    return DistanceInformation(
        distance_vectors=distance_vectors,
        distances=distances,
        neighbor_mask=neighbor_mask,
    )


def calc_psi6(dx: np.ndarray, dy: np.ndarray) -> np.floating:
    angles = np.arctan2(dy, dx)
    psi6 = np.mean(np.exp(1j * 6 * angles))
    return psi6


def calc_psi6_bond_order_given_num_neighbors(
    spheres: HardSpheres, n_neighbors: int
) -> np.ndarray:
    """
    Calculates the psi-6 bond order parameter for each sphere using a fixed number of nearest neighbors.

    Args:
        spheres: An instance of the HardSpheres class.
        n_neighbors: The number of nearest neighbors to use for each sphere.

    Returns:
        A numpy array containing the psi-6 bond order parameter for each sphere.
    """

    psi6_values = np.zeros(spheres.n, dtype=complex)

    d = calc_distance_information(spheres)

    for i in range(spheres.n):
        distances = d.distances[i]
        # Exclude the sphere itself
        distances[i] = np.inf
        nearest_neighbor_indices = np.argsort(distances)[:n_neighbors]

        if nearest_neighbor_indices.size > 1:
            dx = d.distance_vectors[i, nearest_neighbor_indices, 0]
            dy = d.distance_vectors[i, nearest_neighbor_indices, 1]
            psi6_values[i] = calc_psi6(dx, dy)

    return psi6_values
