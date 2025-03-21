use itertools::Itertools;
use ndarray::{Array1, Array2};
use numpy::{PyArray2, ToPyArray};
use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};
use std::ops::AddAssign;

fn isclose(a: f64, b: f64, rel_tol: f64, abs_tol: f64) -> bool {
    // Check for NaN values first
    if a.is_nan() || b.is_nan() {
        return false;
    }

    // Calculate the absolute difference between a and b
    let diff = (a - b).abs();

    // Calculate the maximum of relative tolerance and absolute tolerance
    let allowed_rel_diff = rel_tol * f64::max(a.abs(), b.abs());
    let allowed_diff = f64::max(abs_tol, allowed_rel_diff);

    // Compare the difference with the allowed difference
    diff <= allowed_diff
}
const DEFAULT_REL_TOL: f64 = 1e-9;
const DEFAULT_ABS_TOL: f64 = 0.0;

// Convenience function with default tolerance values
// https://docs.python.org/3/library/math.html#math.isclose
fn isclose_default(a: f64, b: f64) -> bool {
    isclose(a, b, DEFAULT_REL_TOL, DEFAULT_ABS_TOL)
}

#[pyclass]
#[derive(Debug, Clone, Eq, Hash, PartialEq)]
pub struct SphereBoxEvent {
    sphere_id: usize,
    dim: usize,
}

#[pymethods]
impl SphereBoxEvent {
    #[new]
    pub fn new(sphere_id: usize, dim: usize) -> Self {
        SphereBoxEvent { sphere_id, dim }
    }

    fn __str__(&self) -> String {
        format!(
            "SphereBoxEvent(sphere_id={}, dim={})",
            self.sphere_id, self.dim
        )
    }

    fn __repr__(&self) -> String {
        format!(
            "SphereBoxEvent(sphere_id={}, dim={})",
            self.sphere_id, self.dim
        )
    }
}

#[pyclass]
#[derive(Debug, Clone, Eq, Hash, PartialEq)]
pub struct SphereSphereEvent {
    sphere_id0: usize,
    sphere_id1: usize,
}

#[pymethods]
impl SphereSphereEvent {
    #[new]
    pub fn new(sphere_id0: usize, sphere_id1: usize) -> Self {
        assert!(sphere_id0 != sphere_id1);

        SphereSphereEvent {
            sphere_id0,
            sphere_id1,
        }
    }

    fn __str__(&self) -> String {
        format!(
            "SphereSphereEvent(sphere_id0={}, sphere_id0={})",
            self.sphere_id0, self.sphere_id1
        )
    }

    fn __repr__(&self) -> String {
        format!(
            "SphereSphereEvent(sphere_id0={}, sphere_id0={})",
            self.sphere_id0, self.sphere_id1
        )
    }
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct HardSpheres {
    x: Array2<f64>,
    v: Array2<f64>,
    #[pyo3(get)]
    t: f64,
    #[pyo3(get)]
    sigma: f64,
    #[pyo3(get)]
    a: f64,
    m: Array1<f64>,
    #[pyo3(get)]
    dt_snapshot: f64,
    #[pyo3(get)]
    pairs: HashSet<(usize, usize)>,
    #[pyo3(get)]
    ekin: f64,
    #[pyo3(get)]
    t_snapshot: f64,
    #[pyo3(get)]
    d: usize,
    #[pyo3(get)]
    n: usize,
    #[pyo3(get)]
    box_events: Vec<SphereBoxEvent>,
    #[pyo3(get)]
    sphere_events: Vec<SphereSphereEvent>,
}

#[pymethods]
impl HardSpheres {
    #[new]
    pub fn new(
        x: Vec<Vec<f64>>,
        v: Vec<Vec<f64>>,
        t: f64,
        sigma: f64,
        a: f64,
        m: Vec<f64>,
        dt_snapshot: f64,
        t_snapshot: f64,
    ) -> Self {
        let n: usize = x.len();
        assert_eq!(v.len(), n);
        let d: usize = x[0].len();

        // make sure all x entries are of length d
        for i in 0..n {
            assert_eq!(x[i].len(), d);
            assert_eq!(v[i].len(), d);
        }

        let x = Array2::from_shape_vec((n, d), x.into_iter().flatten().collect()).unwrap();
        let v = Array2::from_shape_vec((n, d), v.into_iter().flatten().collect()).unwrap();
        let m = Array1::from(m);

        let pairs = (0..n)
            .combinations(2)
            .map(|pair| (pair[0], pair[1]))
            .collect::<HashSet<_>>();

        HardSpheres {
            x,
            v,
            t,
            sigma,
            a,
            m,
            dt_snapshot,
            pairs,
            ekin: 0.,
            t_snapshot,
            d,
            n,
            box_events: Vec::new(),
            sphere_events: Vec::new(),
        }
    }

    #[getter]
    fn get_x(&self, py: Python) -> PyResult<Py<PyArray2<f64>>> {
        Ok(self.x.clone().to_pyarray(py).into())
    }

    #[getter]
    fn get_v(&self, py: Python) -> PyResult<Py<PyArray2<f64>>> {
        Ok(self.v.clone().to_pyarray(py).into())
    }

    fn __str__(&self) -> String {
        format!(
            "HardSpheres(t={}, sigma={}, a={}, dt_snapshot={}, box_events={:?}, sphere_events={:?})",
            self.t, self.sigma, self.a, self.dt_snapshot, self.box_events, self.sphere_events
        )
    }

    fn __repr__(&self) -> String {
        format!(
            "HardSpheres(x={:?}, v={:?}, t={}, sigma={}, a={}, m={:?}, dt_snapshot={}, pairs={:?}, ekin={}, d={}, n={}, box_events={:?}, sphere_events={:?})",
            self.x, self.v, self.t, self.sigma, self.a, self.m, self.dt_snapshot, self.pairs, self.ekin, self.d, self.n, self.box_events, self.sphere_events
        )
    }

    pub fn clone_hard_spheres(&self) -> Self {
        HardSpheres {
            x: self.x.clone(), // Assuming x is a Vec<Vec<f64>>
            v: self.v.clone(), // Assuming v is a Vec<Vec<f64>>
            t: self.t,
            sigma: self.sigma,
            a: self.a,
            m: self.m.clone(), // Assuming m is a Vec<f64>
            dt_snapshot: self.dt_snapshot,
            pairs: self.pairs.clone(), // Assuming pairs is a field
            ekin: self.ekin,
            t_snapshot: self.t_snapshot,
            d: self.d,
            n: self.n,
            box_events: self.box_events.clone(), // Assuming box_events is a field
            sphere_events: self.sphere_events.clone(), // Assuming sphere_events is a field
        }
    }
}

fn calc_box_events(s: &HardSpheres) -> HashMap<SphereBoxEvent, f64> {
    let mut box_events = HashMap::new();

    for (i, (xi, vi)) in
        s.x.axis_iter(ndarray::Axis(0))
            .zip(s.v.axis_iter(ndarray::Axis(0)))
            .enumerate()
    {
        for d in 0..s.d {
            let x = xi[d];
            let v = vi[d];

            let v_sign = v.signum();
            if v == 0. {
                continue;
            } else if v_sign == 1. {
                let dt = (s.a - s.sigma - x) / v;
                let event = SphereBoxEvent::new(i, d);
                box_events.insert(event, dt);
            } else if v_sign == -1. {
                let dt = (s.sigma - x) / v;
                let event = SphereBoxEvent::new(i, d);
                box_events.insert(event, dt);
            }
        }
    }

    box_events
}

fn calc_sphere_events(s: &HardSpheres) -> HashMap<SphereSphereEvent, f64> {
    let mut sphere_events = HashMap::new();

    for (i, j) in s.pairs.iter() {
        let xi = s.x.row(*i);
        let xj = s.x.row(*j);
        let vi = s.v.row(*i);
        let vj = s.v.row(*j);

        // Calculate relative position and velocity
        let dx = &xi - &xj;
        let dv = &vi - &vj;

        // Calculate the dot product of dx and dv
        let dxdv = dx.dot(&dv);
        let spheres_approaching = dxdv.signum() == -1.;

        let dxs_square = dx.dot(&dx);
        let dvs_square = dv.dot(&dv);

        let root_content = dxdv.powi(2) - dvs_square * (dxs_square - 4. * s.sigma.powi(2));
        let root_sign = root_content.signum();
        let root_is_okay = root_content == 0. || root_sign == 1.;

        let root_is_finite = root_is_okay && spheres_approaching;

        if root_is_finite {
            let root = root_content.sqrt();
            let dt_plus = (-dxdv + root) / dvs_square;
            let dt_minus = (-dxdv - root) / dvs_square;
            let dt;

            if dt_minus < 0. {
                dt = dt_plus;
            } else {
                dt = f64::min(dt_plus, dt_minus);
            }
            assert!(dt >= 0.);
            let event = SphereSphereEvent {
                sphere_id0: *i,
                sphere_id1: *j,
            };
            sphere_events.insert(event, dt);
        }
    }

    sphere_events
}

pub fn update_positions_and_time(s: &mut HardSpheres, dt: f64) {
    s.x += &(&s.v * dt);
    s.t += dt;
}

pub fn update_velocities_through_box_collision(s: &mut HardSpheres) {
    for event in s.box_events.iter() {
        s.v[[event.sphere_id, event.dim]] *= -1.;
    }
}

#[allow(non_snake_case)]
pub fn update_velocities_through_sphere_collision(s: &mut HardSpheres) {
    let v0 = s.v.clone();
    for event in s.sphere_events.iter() {
        let k = event.sphere_id0;
        let l = event.sphere_id1;

        let xk = s.x.row(k);
        let xl = s.x.row(l);
        let vk = s.v.row(k).to_owned();
        let vl = s.v.row(l).to_owned();

        // Calculate relative position and velocity
        let dx = &xk - &xl;
        let dv = &vk - &vl;

        // Calculate the norm of dx
        let r = (dx.mapv(|x| x.powi(2)).sum()).sqrt();

        let e_orthogonal = dx / r;
        let dv_update = &e_orthogonal * dv.dot(&e_orthogonal);

        let m = s.m[k] + s.m[l];
        let Jk = 2. * s.m[l] / m;
        let Jl = 2. * s.m[k] / m;
        s.v.row_mut(k).add_assign(&(-&dv_update * Jk));
        s.v.row_mut(l).add_assign(&(&dv_update * Jl));
    }

    // Check if velocities have changed
    if v0 == s.v {
        panic!("v did not change");
    }
}

fn update_kinetic_energy(s: &mut HardSpheres) {
    let mut ekin = 0.0;

    for i in 0..s.n {
        let v_square = s.v.row(i).map(|&v| v * v).sum();
        ekin += 0.5 * s.m[i] * v_square;
    }

    s.ekin = ekin;
}

pub fn update_box_sphere_events(
    s: &mut HardSpheres,
    box_events: HashMap<SphereBoxEvent, f64>,
    dt_min: f64,
) {
    for (event, &dt) in box_events.iter() {
        if isclose_default(dt, dt_min) {
            s.box_events.push(event.clone());
        }
    }
}

pub fn update_sphere_sphere_events(
    s: &mut HardSpheres,
    sphere_events: HashMap<SphereSphereEvent, f64>,
    dt_min: f64,
) {
    for (event, &dt) in sphere_events.iter() {
        if isclose_default(dt, dt_min) {
            s.sphere_events.push(event.clone());
        }
    }
}

pub fn clear_events(s: &mut HardSpheres) {
    s.box_events.clear();
    s.sphere_events.clear();
}

pub fn calc_min_dts(
    box_events: &HashMap<SphereBoxEvent, f64>,
    sphere_events: &HashMap<SphereSphereEvent, f64>,
) -> (f64, f64, f64) {
    let dt_box_min = box_events.values().cloned().fold(f64::INFINITY, f64::min);
    let dt_sphere_min = sphere_events
        .values()
        .cloned()
        .fold(f64::INFINITY, f64::min);
    let dt_collision = f64::min(dt_box_min, dt_sphere_min);

    (dt_collision, dt_box_min, dt_sphere_min)
}

#[pyfunction]
pub fn update_spheres_from_bin(s: &mut HardSpheres) -> Vec<HardSpheres> {
    let mut history = Vec::<HardSpheres>::new();

    clear_events(s);

    let box_events = calc_box_events(&s);
    let sphere_events = calc_sphere_events(&s);

    let (mut dt_collision, dt_box_min, dt_sphere_min) = calc_min_dts(&box_events, &sphere_events);

    let t_collision = s.t + dt_collision;

    while s.t_snapshot < t_collision {
        update_positions_and_time(s, s.dt_snapshot);
        history.push(s.clone());
        s.t_snapshot += s.dt_snapshot;
        dt_collision -= s.dt_snapshot;
    }

    update_positions_and_time(s, dt_collision);

    let is_sphere_collision = dt_box_min > dt_sphere_min;

    if is_sphere_collision {
        update_sphere_sphere_events(s, sphere_events, dt_sphere_min);
        update_velocities_through_sphere_collision(s);
    } else {
        update_box_sphere_events(s, box_events, dt_box_min);
        update_velocities_through_box_collision(s);
    }

    update_kinetic_energy(s);

    history
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_update_spheres_components() {
        // let mut _rng = rand::thread_rng();

        let x = vec![vec![0.2, 0.15], vec![0.85, 0.85], vec![0.4, 0.2]];

        let v = vec![vec![0.2, 0.2], vec![-0.15, -0.15], vec![0.0, 0.1]];

        let t = 0.0;
        let sigma = 0.1; // Diameter of the spheres
        let a = 1.0; // Length of the simulation box (assuming cubic for simplicity)
        let m = vec![1.0, 1.0, 1.0]; // Masses of the spheres
        let dt_snapshot = 0.01;
        let t_snapshot = 0.;

        let mut s = HardSpheres::new(x, v, t, sigma, a, m, dt_snapshot, t_snapshot);

        // run the components of update_sphere
        let box_events = calc_box_events(&s);
        assert!(box_events.len() > 0);

        let sphere_events = calc_sphere_events(&s);
        assert!(sphere_events.len() > 0);

        let (mut dt_collision, dt_box_min, dt_sphere_min) =
            calc_min_dts(&box_events, &sphere_events);
        assert!(dt_box_min > 0.);
        assert!(dt_sphere_min > 0.);
        assert!(dt_collision > 0.);

        let t_collision = s.t + dt_collision;
        let mut t_snapshot = s.t + s.dt_snapshot;

        let mut history = Vec::<HardSpheres>::new();
        let dt_snapshot = s.dt_snapshot;
        while t_snapshot < t_collision {
            update_positions_and_time(&mut s, dt_snapshot);
            history.push(s.clone());
            t_snapshot += dt_snapshot;
            dt_collision -= dt_snapshot;
        }

        assert!(
            history.len() > 0,
            "number of snapshots {num}",
            num = history.len()
        );

        update_positions_and_time(&mut s, dt_collision);

        let is_box_collision = dt_box_min < dt_sphere_min;

        if is_box_collision {
            update_box_sphere_events(&mut s, box_events, dt_box_min);
            update_velocities_through_box_collision(&mut s);
        } else {
            update_sphere_sphere_events(&mut s, sphere_events, dt_sphere_min);
            update_velocities_through_sphere_collision(&mut s);
        }

        update_kinetic_energy(&mut s);
        assert!(s.ekin > 0.);
    }

    #[test]
    fn test_update_spheres() {
        // let mut _rng = rand::thread_rng();

        // Initialize spheres
        let x = vec![vec![0.2, 0.15], vec![0.85, 0.85], vec![0.4, 0.2]];

        let v = vec![vec![0.2, 0.2], vec![-0.15, -0.15], vec![0.0, 0.1]];

        let t = 0.0;
        let sigma = 0.1; // Diameter of the spheres
        let a = 1.0; // Length of the simulation box (assuming cubic for simplicity)
        let m = vec![1.0, 1.0, 1.0]; // Masses of the spheres
        let dt_snapshot = 0.1;
        let t_snapshot = 0.;

        let mut s = HardSpheres::new(x, v, t, sigma, a, m, dt_snapshot, t_snapshot);

        let mut history: Vec<HardSpheres> = Vec::new();

        for _ in 0..5 {
            let _h = update_spheres_from_bin(&mut s);
            history.extend_from_slice(&_h);
        }

        assert!(history.len() > 0);
    }

    #[test]
    fn test_isclose_default() {
        assert!(isclose_default(1.0000000000000001, 1.0));
        assert!(isclose_default(1.0, 0.9999999999999998));
        assert!(!isclose_default(1.0, 2.0));
        assert!(!isclose_default(2.0, 1.0));
    }
}
