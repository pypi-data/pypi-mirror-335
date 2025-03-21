use pyo3::prelude::*;
mod spheres;

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<spheres::SphereBoxEvent>()?;
    m.add_class::<spheres::SphereSphereEvent>()?;
    m.add_class::<spheres::HardSpheres>()?;
    m.add_function(wrap_pyfunction!(spheres::update_spheres_from_bin, m)?)?;

    Ok(())
}
