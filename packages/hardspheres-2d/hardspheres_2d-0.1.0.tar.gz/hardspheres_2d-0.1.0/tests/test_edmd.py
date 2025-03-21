import random

import numpy as np

from hardspheres_2d import HardSpheres, update_spheres
from hardspheres_2d.util import (
    count_consecutive_changes_in_acceleration,
    dataframify_history_2d_trajectories,
)


def test_update_spheres():
    SEED = 42
    random.seed(SEED)

    n_iter = 500
    n_spheres = 5 * 8

    sigma = 0.01
    a = 1.0
    dt_snaphot = 0.01

    x = [[random.uniform(a=0, b=1) for _ in range(2)] for _ in range(n_spheres)]
    v = [[random.uniform(a=-0.2, b=0.2) for _ in range(2)] for _ in range(n_spheres)]

    s = HardSpheres(
        x=x,
        v=v,
        t=0.0,
        sigma=sigma,
        a=a,
        m=list(np.ones(n_spheres)),
        dt_snapshot=dt_snaphot,
        t_snapshot=0.0,
    )
    assert isinstance(s, HardSpheres)

    history = []

    for _ in range(n_iter):
        _history = update_spheres(s)
        history.extend(_history)

    df_trajectories = dataframify_history_2d_trajectories(history)
    df_trajectories = count_consecutive_changes_in_acceleration(df_trajectories)

    assert df_trajectories["n_consecutive_acceleration_changes"].max() <= 2  # type: ignore
