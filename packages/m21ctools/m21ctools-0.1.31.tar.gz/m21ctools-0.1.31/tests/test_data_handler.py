import os
import sys
import tempfile
import numpy as np
import xarray as xr
import pytest

# Ensure that the project root is on the sys.path so that the m21ctools package is found.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from m21ctools.data_handler import CubedSphereData

@pytest.fixture
def temp_nc4_file():
    nf = 6
    Ydim = 5
    Xdim = 5
    ncontact = 4

    # Generate dummy data
    lats = np.random.uniform(-90, 90, size=(nf, Ydim, Xdim))
    lons = np.random.uniform(0, 360, size=(nf, Ydim, Xdim))
    qv_data = np.random.rand(nf, Ydim, Xdim)

    # Create an xarray.Dataset mimicking the expected structure
    ds = xr.Dataset(
        {
            "QV": (("time", "lev", "nf", "Ydim", "Xdim"), qv_data[np.newaxis, np.newaxis, ...]),
            "lats": (("nf", "Ydim", "Xdim"), lats),
            "lons": (("nf", "Ydim", "Xdim"), lons),
            "anchor": (("nf", "ncontact", "ncontact"), np.zeros((nf, ncontact, ncontact), dtype=int))
        },
        coords={
            "time": np.array(["2020-01-01"], dtype="datetime64[ns]"),
            "lev": np.array([1000.0]),
            "nf": np.arange(1, nf + 1),
            "Ydim": np.linspace(-90, 90, Ydim),
            "Xdim": np.linspace(0, 360, Xdim),
            "ncontact": np.arange(1, ncontact + 1)
        }
    )

    # Write the dataset to a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".nc4", delete=False)
    ds.to_netcdf(temp_file.name, engine="h5netcdf")
    temp_file.close()

    yield temp_file.name

    # Cleanup the temporary file after the test
    os.remove(temp_file.name)

def test_load_data(temp_nc4_file):
    # Instantiate the CubedSphereData, which automatically loads the data.
    cs_data = CubedSphereData(temp_nc4_file, time=0, lev=0, variable="QV")

    # Assert that key attributes have been set.
    assert cs_data.lats is not None, "lats should not be None after loading data"
    assert cs_data.lons is not None, "lons should not be None after loading data"
    assert cs_data.data is not None, "data should not be None after loading data"

    # Check that the data has 6 faces.
    assert cs_data.data.shape[0] == 6, "There should be 6 faces in the data"

    # Check aggregated data lengths: nf * Ydim * Xdim should equal 6 * 5 * 5.
    expected_length = 6 * 5 * 5
    assert len(cs_data.all_lats) == expected_length, "Aggregated lats length does not match expected value"
    assert len(cs_data.all_lons) == expected_length, "Aggregated lons length does not match expected value"
    assert len(cs_data.all_data) == expected_length, "Aggregated data length does not match expected value"

    # Ensure longitudes are adjusted to the range [-180, 180].
    assert np.all((cs_data.lons >= -180) & (cs_data.lons <= 180)), "Longitudes should be within [-180, 180]"

def test_aggregate_data(temp_nc4_file):
    # Instantiate the CubedSphereData object.
    cs_data = CubedSphereData(temp_nc4_file, time=0, lev=0, variable="QV")
    
    # Explicitly call the aggregate_data() method.
    all_lats, all_lons, all_data = cs_data.aggregate_data()
    
    # Get the dimensions from the loaded data (data shape: (nf, Ydim, Xdim))
    nf, Ydim, Xdim = cs_data.data.shape
    expected_length = nf * Ydim * Xdim
    
    # Verify that the length of each aggregated list matches the expected length.
    assert len(all_lats) == expected_length, "Aggregated lats length is not as expected."
    assert len(all_lons) == expected_length, "Aggregated lons length is not as expected."
    assert len(all_data) == expected_length, "Aggregated data length is not as expected."
    
    # Manually compute expected aggregated values by flattening each face.
    expected_lats = []
    expected_lons = []
    expected_data = []
    for face in range(nf):
        expected_lats.extend(cs_data.lats[face, :, :].flatten())
        expected_lons.extend(cs_data.lons[face, :, :].flatten())
        expected_data.extend(cs_data.data[face, :, :].flatten())
    
    # Compare numerical arrays using numpy.testing.assert_allclose.
    np.testing.assert_allclose(np.array(all_lats), np.array(expected_lats),
                               err_msg="Aggregated latitudes do not match expected values.")
    np.testing.assert_allclose(np.array(all_lons), np.array(expected_lons),
                               err_msg="Aggregated longitudes do not match expected values.")
    np.testing.assert_allclose(np.array(all_data), np.array(expected_data),
                               err_msg="Aggregated data values do not match expected values.")


