import numpy as np
import polars as pl

from hardspheres_2d import HardSpheres


def calc_magnitudes(vecs: list[np.ndarray]) -> list[np.ndarray]:
    return [np.linalg.norm(v, axis=1, ord=2) for v in vecs]


def calc_accelerations(
    history: list[HardSpheres], by_sphere: bool = False
) -> list[np.ndarray]:
    accelerations = [
        (h1.v - h0.v) / (h1.t - h0.t)
        for h1, h0 in zip(history[1:], history[:-1], strict=True)
    ]
    if by_sphere:
        n_spheres = accelerations[0].shape[0]
        n_steps = len(accelerations)
        accelerations = [
            np.array(
                [accelerations[step][sphere, :] for step in range(n_steps)], dtype=float
            )
            for sphere in range(n_spheres)
        ]

    return accelerations


def calc_velocity_angles(
    history: list[HardSpheres], by_sphere: bool = False
) -> list[np.ndarray]:
    angles = [
        (h1.v * h0.v).sum(axis=1)
        / np.linalg.norm(h1.v, axis=1, ord=2)
        / np.linalg.norm(h0.v, axis=1, ord=2)
        for h1, h0 in zip(history[1:], history[:-1], strict=True)
    ]
    if by_sphere:
        n_spheres = angles[0].shape[0]
        n_steps = len(angles)
        angles = [
            np.array([angles[step][sphere] for step in range(n_steps)], dtype=float)
            for sphere in range(n_spheres)
        ]
    return angles


def dataframify_history_2d_trajectories(history: list[HardSpheres]) -> pl.DataFrame:
    """
    Returns a DataFrame with one row per hard sphere and time step, containing coordinates,
    velocity magnitude, and acceleration magnitude.
    """

    dicts = []

    accelerations = calc_accelerations(history, by_sphere=False)
    acceleration_magnitudes = calc_magnitudes(accelerations)
    angles = calc_velocity_angles(history, by_sphere=False)

    for t_step, spheres in enumerate(history):
        if t_step == 0:
            continue

        v_magnitudes = np.linalg.norm(spheres.v[:, :2], ord=2, axis=1)

        for sphere_id in range(spheres.n):
            dicts.append(
                {
                    "time": spheres.t,
                    "iteration": t_step,
                    "sphere_id": sphere_id,
                    "x": spheres.x[sphere_id, 0],
                    "y": spheres.x[sphere_id, 1],
                    "v_x": spheres.v[sphere_id, 0],
                    "v_y": spheres.v[sphere_id, 1],
                    "a_x": accelerations[t_step - 1][sphere_id, 0],
                    "a_y": accelerations[t_step - 1][sphere_id, 1],
                    "v_magnitude": v_magnitudes[sphere_id],
                    "a_magnitude": acceleration_magnitudes[t_step - 1][sphere_id],
                    "angle": angles[t_step - 1][sphere_id],
                }
            )

    df = pl.from_dicts(dicts)

    return df


def count_consecutive_changes_in_acceleration(df: pl.DataFrame) -> pl.DataFrame:
    """
    Example:

    df0 = pl.DataFrame({
        "sphere_id": [0,0,0,0,0,0],
        "time": [1,2,3,4,5,6],
        "a_magnitude": [0,1,1,.5,0,.2],
    },pl.Schema({"sphere_id":pl.Int64, "time":pl.Int64,"a_magnitude":pl.Float64}))
    df1 = pl.DataFrame({
        "sphere_id": [1,1,1],
        "time": [1,2,3],
        "a_magnitude": [0,0,0],
    }, schema=pl.Schema({"sphere_id":pl.Int64, "time":pl.Int64,"a_magnitude":pl.Float64}))
    df = pl.concat((df0,df1),how="vertical")
    df = df.sort(("time","sphere_id"))
    df = ch2py.count_consecutive_changes_in_acceleration(df)

    df.filter(pl.col("sphere_id").eq(0))
    df.filter(pl.col("sphere_id").eq(1))
    """

    df = df.with_columns((pl.col("a_magnitude") > 0).alias("a_changed"))

    df = df.with_columns(
        pl.when(pl.col("a_changed"))
        .then(1)
        .otherwise(0)
        .cum_sum()
        .over("sphere_id", order_by="time")
        .alias("a_cumsum")
    )

    df = df.with_columns(
        pl.when(pl.col("a_changed").shift().eq(pl.col("a_changed").not_()))
        .then(1)
        .otherwise(0)
        .over("sphere_id", order_by="time")
        .alias("change_mark")
    )

    df = df.with_columns(
        pl.col("change_mark")
        .cum_sum()
        .over("sphere_id", order_by="time")
        .alias("change_id")
    )

    min_by_group = (
        df.group_by(["sphere_id", "change_id"])
        .agg(pl.col("a_cumsum").min().alias("a_cumsum_min"))
        .select(["sphere_id", "change_id", "a_cumsum_min"])
    )

    df = df.join(min_by_group, on=["sphere_id", "change_id"], how="left")
    df = df.with_columns(
        (pl.col("a_cumsum") - pl.col("a_cumsum_min")).alias(
            "n_consecutive_acceleration_changes"
        )
    )

    df = df.drop(["a_changed", "a_cumsum", "change_mark", "change_id", "a_cumsum_min"])

    return df


def listify_array(x: np.ndarray) -> list[list[float]] | list[float]:
    if x.ndim == 2:
        return [list(v) for v in x]
    elif x.ndim == 1:
        return list(x)
    else:
        raise NotImplementedError(f"{x.ndim=} > 2, not implemented.")
