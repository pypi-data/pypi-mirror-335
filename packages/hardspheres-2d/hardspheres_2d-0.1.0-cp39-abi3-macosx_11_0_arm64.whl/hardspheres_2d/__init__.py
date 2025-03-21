import math
from dataclasses import dataclass

import numpy as np
import tqdm

from hardspheres_2d._core import HardSpheres, update_spheres_from_bin
from hardspheres_2d.psi6 import calc_psi6_bond_order_given_num_neighbors


def update_spheres(s: HardSpheres) -> list[HardSpheres]:
    return update_spheres_from_bin(s)


def generate_velocities(
    m: np.ndarray, dim: int, T: float, kb: float = 1.0, seed: int = 42
) -> np.ndarray:
    n = len(m)
    if np.unique(m).shape[0] == 1:
        m = m[0]
    else:
        raise NotImplementedError(
            "Not yet implemented a sampling of velocities for spheres with different masses."
        )
    std_dev = math.sqrt(kb * T / m)
    rng = np.random.RandomState(seed=seed)
    velocities = rng.normal(0, std_dev, size=(n, dim))

    return velocities


@dataclass
class PerturbedSpheres:
    spheres: HardSpheres
    std: float
    psi6: np.ndarray


def run_edmd(
    s: HardSpheres,
    n_iter: int,
    T: float,
    progress: bool,
    return_extra_info: bool = False,
) -> tuple[list[HardSpheres], list[np.ndarray], list[PerturbedSpheres]]:
    history_spheres = []
    history_psi6_abs_n = []
    history_perturbed_spheres = []

    disable = not progress

    for _ in tqdm.tqdm(
        range(n_iter), total=n_iter, desc="Collision", miniters=100, disable=disable
    ):
        _history = update_spheres(s)
        _psi6s = [
            np.abs(calc_psi6_bond_order_given_num_neighbors(_s, n_neighbors=6))
            for _s in _history
        ]
        if return_extra_info:
            _perturbed_history = [
                PerturbedSpheres(_h, T, psi6=_psi6)
                for _h, _psi6 in zip(_history, _psi6s, strict=True)
            ]

        history_spheres.extend(_history)
        history_psi6_abs_n.extend(_psi6s)
        if return_extra_info:
            history_perturbed_spheres.extend(_perturbed_history)  # type: ignore

    return history_spheres, history_psi6_abs_n, history_perturbed_spheres
