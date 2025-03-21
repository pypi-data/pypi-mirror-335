use coord_transforms::prelude::Vector3;
use pyo3::prelude::*;

#[pyclass]
struct GeoEllipsoid {
    inner: coord_transforms::structs::geo_ellipsoid::geo_ellipsoid,
}

#[pyfunction]
fn wgs84() -> PyResult<GeoEllipsoid> {
    let inner = coord_transforms::structs::geo_ellipsoid::geo_ellipsoid::new(
        coord_transforms::structs::geo_ellipsoid::WGS84_SEMI_MAJOR_AXIS_METERS,
        coord_transforms::structs::geo_ellipsoid::WGS84_FLATTENING,
    );
    Ok(GeoEllipsoid { inner })
}

#[pyfunction]
fn ned2lla(
    lat0: f64,
    lon0: f64,
    alt0: f64,
    north_m: f64,
    east_m: f64,
    down_m: f64,
    geo_ellipsoid: &GeoEllipsoid,
) -> PyResult<(f64, f64, f64)> {
    let lla0 = Vector3::new(lat0, lon0, alt0);
    let ned = Vector3::new(north_m, east_m, down_m);
    let lla = coord_transforms::geo::ned2lla(&lla0, &ned, &geo_ellipsoid.inner);
    Ok((lla[0], lla[1], lla[2]))
}

#[pyfunction]
fn lla2ned(
    lat0: f64,
    lon0: f64,
    alt0: f64,
    lat: f64,
    lon: f64,
    alt: f64,
    geo_ellipsoid: &GeoEllipsoid,
) -> PyResult<(f64, f64, f64)> {
    let lla0 = Vector3::new(lat0, lon0, alt0);
    let lla = Vector3::new(lat, lon, alt);
    let ned = coord_transforms::geo::lla2ned(&lla0, &lla, &geo_ellipsoid.inner);
    Ok((ned[0], ned[1], ned[2]))
}

/// A Python module implemented in Rust.
#[pymodule]
fn pyned2lla(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(ned2lla, m)?)?;
    m.add_function(wrap_pyfunction!(lla2ned, m)?)?;
    m.add_function(wrap_pyfunction!(wgs84, m)?)?;
    Ok(())
}
