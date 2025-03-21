from pathlib import Path

import click
import numpy as np

from hardspheres_2d import HardSpheres, generate_velocities, run_edmd
from hardspheres_2d.dump import write_xyz_file
from hardspheres_2d.hex import place_spheres_hexagonal
from hardspheres_2d.util import listify_array


@click.command()
@click.option("--temperature", "-T", default=0.01, help="Temperature of the system.")
@click.option("--radius", "-r", default=0.5, help="Radius of each hard sphere.")
@click.option(
    "--iterations",
    "-i",
    default=1000,
    help="Number of iterations to run the simulation.",
)
@click.option(
    "--dt-snapshot",
    "-dt",
    default=0.01,
    help="Snapshot interval for writing to .xyz file.",
)
@click.option(
    "--edge-length", "-a", default=10.0, help="Edge length of the simulation box."
)
@click.option(
    "--edge-factor",
    default=1.1,
    help="Factor to multiply the edge-length with to get the simulation box size.",
)
@click.option("--gap", default=0.1, help="Gap between spheres in x and y.")
@click.option(
    "--output-file",
    "-o",
    default="simulation.xyz",
    help="Output file name for results.",
)
@click.option(
    "--progress",
    default=True,
    help="Flag to activate / deactivate the progress bar for the EDMD simulation.",
)
@click.option("--seed", default=42, help="Seed for the sampling of the velocities.")
def main(
    temperature: float,
    radius: float,
    iterations: int,
    dt_snapshot: float,
    edge_length: float,
    edge_factor: float,
    gap: float,
    output_file: Path,
    progress: bool,
    seed: int,
):
    print(f"Contructing hard spheres: {edge_length=}, {edge_factor=} and {gap=}")
    sphere_centers = place_spheres_hexagonal(edge_length, radius, gap=gap)
    m = np.ones(shape=len(sphere_centers))

    print(f"Generating velocities for {temperature=}")
    velocities = generate_velocities(m, 2, temperature, seed)

    # Listify arrays
    x = listify_array(sphere_centers)
    v = listify_array(velocities)
    m = listify_array(np.ones(shape=len(x)))

    # Initialize HardSpheres object
    s = HardSpheres(
        x=x,  # type: ignore
        v=v,  # type: ignore
        t=0.0,
        sigma=radius,
        a=edge_length * edge_factor,
        m=m,  # type: ignore
        dt_snapshot=dt_snapshot,
        t_snapshot=0.0,
    )

    # Run the simulation and write results to .xyz file
    print(
        f"Running Event Driven Molecular Dynamics Simulation for {iterations=:_} with {progress=}"
    )
    history_spheres, history_psi6_abs_n, _ = run_edmd(
        s, n_iter=iterations, T=temperature, progress=progress, return_extra_info=False
    )

    file = Path(output_file)

    print(f"Writing {len(history_spheres):_} snapshots to {file}")
    write_xyz_file(
        history_spheres,
        file,
        sphere_features={
            "psi6_n_abs": history_psi6_abs_n,
        },
    )


if __name__ == "__main__":
    main()
