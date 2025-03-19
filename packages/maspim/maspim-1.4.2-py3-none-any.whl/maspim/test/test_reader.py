import numpy as np

import os

from maspim import ReadBrukerMCF, hdf5Handler
from maspim.project.file_helpers import get_d_folder

path_folder = r'C:\Users\Yannick Zander\Promotion\Test data'
path_d_folder = os.path.join(path_folder, get_d_folder(path_folder))


def test_readbrukermcf():
    reader = ReadBrukerMCF(path_d_folder)
    reader.create_reader()

    reader.create_indices()
    indices = np.arange(1, 72 + 1)
    assert reader.indices.shape == indices.shape
    assert np.allclose(reader.indices, indices)

    reader.set_meta_data()
    assert reader.metaData.shape == (348, 5)

    reader.set_casi_window()
    assert reader.limits == (544., 564)

    spec = reader.get_spectrum(1)
    assert np.allclose(spec.intensities, np.load('test_spectrum.npy'))

    reader.create_spots()
    spot = reader.spots.names[0]
    assert spot == 'R00X082Y054'

    spec_spot = reader.get_spectrum_by_spot(spot)
    assert np.allclose(spec_spot.intensities, np.load('test_spectrum.npy'))

    reader.set_mzs(np.arange(reader.limits[0], reader.limits[1], 1e-4))
    reader.get_spectrum_resampled_intensities(1)

    # no longer method of reader
    # apply_calibration(spec, [0.5, -.2, 0])


def test_hdf5_creation():
    """Check against saved file."""
    reader = ReadBrukerMCF(path_d_folder)
    reader.create_reader()
    reader.create_indices()
    reader.set_meta_data()
    reader.set_casi_window()

    hdf_test = hdf5Handler(os.path.join(path_d_folder, 'test.hdf5'))
    hdf_test.write(reader)

    hdf_benchmark = hdf5Handler(os.path.join(path_d_folder, 'benchmark.hdf5'))
    out_test = hdf_test.read()
    out_bench = hdf_benchmark.read()

    for k, v in out_bench.items():
        assert np.allclose(out_test[k], out_bench[k])


