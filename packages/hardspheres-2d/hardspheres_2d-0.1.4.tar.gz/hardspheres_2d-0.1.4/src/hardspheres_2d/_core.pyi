from __future__ import annotations

import numpy as np

class SphereBoxEvent:
    sphere_id: int
    dim: int

    def __new__(cls, sphere_id: int, dim: int): ...

class SphereSphereEvent:
    sphere_id0: int
    sphere_id1: int

    def __new__(cls, sphere_id0: int, sphere_id1: int): ...

class HardSpheres:
    x: np.ndarray
    v: np.ndarray
    t: float
    sigma: float
    a: float
    m: np.ndarray
    dt_snapshot: float
    pairs: set[tuple[int, int]]
    ekin: float
    t_snapshot: float
    d: int
    n: int

    def __new__(
        cls,
        x: list[list[float]],
        v: list[list[float]],
        t: float,
        sigma: float,
        a: float,
        m: list[float],
        dt_snapshot: float,
        t_snapshot: float,
    ): ...
    def clone_hard_spheres(self) -> HardSpheres: ...

def update_spheres_from_bin(s: HardSpheres) -> list[HardSpheres]: ...
