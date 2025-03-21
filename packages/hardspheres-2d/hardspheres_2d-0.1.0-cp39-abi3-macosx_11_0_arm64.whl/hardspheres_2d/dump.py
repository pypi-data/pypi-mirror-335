import logging
from pathlib import Path

import numpy as np

from hardspheres_2d import HardSpheres

logger = logging.getLogger(__name__)


def write_xyz_file(
    history: list[HardSpheres],
    filename: Path,
    default_element: str = "C",
    sphere_features: dict[str, list[np.ndarray]] | None = None,
):
    """Writes a list of HardSpheres instances to an XYZ file: https://en.wikipedia.org/wiki/XYZ_file_format."""

    logger.info(f"Writing to {filename=}")

    with filename.open("w") as f:
        for i_t, snapshot in enumerate(history):
            f.write(f"{snapshot.n}\n")  # number of spheres
            f.write(f"t={snapshot.t}\n")  # comment line
            for i_sphere in range(snapshot.n):
                # Write the element symbol (e.g., "H")
                f.write(f"{default_element} ")

                # Write the x, y, and z coordinates
                item = f"{snapshot.x[i_sphere, 0]:.6f} {snapshot.x[i_sphere, 1]:.6f} {0.0:.6f}"

                if sphere_features:
                    for k in sphere_features:
                        val = sphere_features[k][i_t][i_sphere]
                        item = f"{item} {val:.6f}"

                item = f"{item}\n"
                f.write(item)  # Assuming z=0 for 2D simulation

    logger.info(f"XYZ file '{filename}' written successfully.")
