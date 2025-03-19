import os
import unittest

import numpy as np

from maspim.project.file_helpers import get_d_folder
from maspim import hdf5Handler, Spectra
from maspim.res.compound_masses import mC37_3, mC37_2, mPyro

path_folder = r'C:\Users\Yannick Zander\Promotion\Test data'
# path_folder = r'C:\Users\Yannick Zander\Promotion\Cariaco MSI 2024\490-495cm\2018_08_27 Cariaco 490-495 alkenones.i'
path_d_folder = os.path.join(path_folder, get_d_folder(path_folder))

reader = hdf5Handler(path_d_folder)


def test_spectra():
    spec = Spectra(path_d_folder=path_d_folder, reader=reader)

    # __init__
    assert spec.delta_mz == 1e-4
    assert np.allclose(spec.limits, (544., 564.))
    idcs = np.arange(1, 72 + 1)
    assert np.allclose(
        np.arange(spec.limits[0], spec.limits[1] + spec.delta_mz * 2, spec.delta_mz),
        spec.mzs
    )
    assert spec.indices.shape == idcs.shape
    assert np.allclose(spec.indices, idcs)
    assert os.path.samefile(spec.path_d_folder, path_d_folder)

    # other stuff
    i = np.ones_like(spec.mzs)
    spec.add_spectrum(i)
    assert np.allclose(spec.intensities, i)
    spec.reset_intensities()
    assert np.allclose(spec.intensities, np.zeros_like(spec.mzs))

    spec.add_all_spectra(reader=reader)
    assert np.allclose(np.load('summed_intensities.npy'), spec.intensities)

    spec.set_noise_level()
    assert np.allclose(np.load('noise_level.npy'), spec.noise_level)

    spec.subtract_baseline()
    tc = unittest.TestCase()
    with tc.assertRaises(AssertionError):
        spec.subtract_baseline()

    shift = spec.get_mass_shift(reader.get_spectrum(5))
    assert abs(shift - -0.0003) < 1e-12

    spec.set_peaks()
    assert np.allclose(np.load('test_peaks.npy'), spec._peaks)

    spec.set_targets([mC37_2, mC37_3], method='area', reader=reader)
    spec.set_targets([mC37_2, mC37_3], method='height', reader=reader)
    spec.set_targets([mC37_2, mC37_3], method='max', reader=reader)

def test_peak_filtering():
    spec = Spectra(path_d_folder=path_d_folder, reader=reader)
    spec._intensities = np.load('summed_intensities.npy')
    spec.subtract_baseline()

    # whitelist
    targets = [mC37_2, mC37_3, mPyro]
    spec.set_peaks()
    whitelist = spec._peaks[[np.argmin(np.abs(spec.mzs[spec._peaks] - target)) 
                             for target in targets]]
    spec.filter_peaks(whitelist=whitelist)
    assert len(spec._peaks) == 3

    # snr
    spec.set_peaks()
    spec.filter_peaks(peaks_snr_threshold=1)
    
    # side-peaks
    spec.set_peaks()
    spec.filter_peaks(remove_side_peaks=True)
    
    # side-sigma
    spec.set_peaks()
    spec.set_kernels(suppress_warnings=True)
    spec.filter_peaks(thr_sigma=[2e-3, 10e-3])
    
    # all
    spec.set_peaks()
    spec.set_kernels(suppress_warnings=True, discard_invalid=False)
    spec.filter_peaks(peaks_snr_threshold=1, remove_sidepeaks=True, thr_sigma=[2e-3, 10e-3])

if __name__ == '__main__':
    pass

    # spec = Spectra(path_d_folder=path_d_folder, reader=reader)
    # spec._intensities = np.load('summed_intensities.npy')
    # spec.subtract_baseline()
    
    # import logging
    # logging.basicConfig(level=logging.INFO)
    # spec.set_peaks()
    # spec.set_kernels(suppress_warnings=True, discard_invalid=False)
    
    # spec.plot_summed()
    # spec.filter_peaks(peaks_snr_threshold=1, remove_sidepeaks=True, thr_sigma=[2e-3, 10e-3])
    # spec.plot_summed()
    




