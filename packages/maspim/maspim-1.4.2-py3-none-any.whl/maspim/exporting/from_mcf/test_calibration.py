import matplotlib.pyplot as plt
import numpy as np
from maspim.exporting.from_mcf.spectrum import gaussian

from maspim.res.compound_masses import mC37_2, mC37_3, mPyro

from maspim import Spectra, hdf5Handler, get_project
from maspim.exporting.from_mcf.helper import find_polycalibration_spectrum, apply_calibration, Spectrum
from maspim.res.calibrants import get_calibrants


def plot_calibration(spec, polycoeffs, calibrants, window=.1, ax: plt.Axes | None = None):
    if len(calibrants) == 0:
        print('no calibrants found, cant hsow anything')
        return

    if ax is None:
        _, ax = plt.subplots()

    mask = np.ones(spec.mzs.shape[0], dtype=bool)
    # for c in calibrants:
    #     mask |= (spec.mzs > c - window / 2) & (spec.mzs < c + window / 2)
    ax.plot(spec.mzs[mask], spec.intensities[mask], label='uncalibrated')
    spec_calib = apply_calibration(spec, polycoeffs, False)
    ax.plot(spec_calib.mzs[mask], spec_calib.intensities[mask], label='calibrated')
    
    ymax = spec.intensities[mask].max()
    calibrants_pos = np.zeros(mask.shape[0], dtype=bool)
    for c in calibrants:
        idx = np.argmin(np.abs(c - spec.mzs))
        calibrants_pos[idx] = True
    
    calibrants_mz = spec.mzs[calibrants_pos]
    ax.vlines(calibrants_mz, 0, ymax, colors='k', label='calibrants')
    deg = len(polycoeffs) - 1
    ax.set_title(" + ".join([f'{polycoeffs[i]:.3f} * x^{deg - i}' for i in range(deg + 1)]))
    ax.legend()

    return ax

def synthetic_shifted_spectrum(shift):
    """shifted by constant"""
    mzs = np.arange(mC37_3 - 1, mPyro + 1, 1e-4)
    mz_peaks = np.array([mC37_2, mC37_3, mPyro])
    signal = np.zeros_like(mzs)
    for p in mz_peaks:
        signal += gaussian(mzs, p, 20000, 3e-3)
    mzs += shift
    spec = Spectrum((mzs, signal))
    return spec


def synthetic_poly_spectrum(a, b, shift):
    """mzs are transformed with 2nd degree polynomial"""
    mzs = np.arange(mC37_3 - 1, mPyro + 1, 1e-4)
    mz_peaks = np.array([mC37_2, mC37_3, mPyro])
    signal = np.zeros_like(mzs)
    for p in mz_peaks:
        signal += gaussian(mzs, p, 20000, 3e-3)
    mzs = mzs + (a * mzs ** 2 + b * mzs + shift)
    spec = Spectrum((mzs, signal))
    return spec


def test_synthetic_offset(a=0, b=0, shift=0):
    _spec = synthetic_poly_spectrum(a, b, shift)
    cbr_mzs = np.array(get_calibrants((_spec.mzs.min(), _spec.mzs.max())))

    polycoeffs, n_coeffs, calibs_found = find_polycalibration_spectrum(
        mzs=_spec.mzs,
        intensities=_spec.intensities,
        calibrants_mz=cbr_mzs,
        search_range=5e-3,
        calib_snr_threshold=4,
        noise_level=np.zeros_like(_spec.mzs),
        min_height=10000,
        nearest=False,
        max_degree=1)

    return plot_calibration(_spec, polycoeffs, cbr_mzs[calibs_found])


def test_small_example(plts: bool = False):
    """
    Do binning once with and once without calibration. With calibration the
    intensities should get bigger
    """
    # folder = r'\\hlabstorage.dmz.marum.de\scratch\Yannick\13012023_SBB_TG3A_05-10_Test2'
    folder = r'C:\Users\Yannick Zander\Downloads\maspim workshop\data\small example'
    p = get_project(True, folder)
    reader = p.require_hdf_reader()
    p.set_spectra(reader=reader, full=False)
    spec = p.spectra

    targets = [mC37_2, mC37_3]

    # without calibration
    spec.add_all_spectra(reader)
    spec.subtract_baseline()
    axs = spec.set_targets(
        targets,
        method_peak_center='closest',  # take intensity at theorethical positions
        method='max',
        reader=reader,
        plts=plts, suppress_warnings=True
    )
    axs[1].vlines(targets, 0, 2e7)
    plt.show()

    without_calib = spec.feature_table.mean()

    # with calibration
    spec.add_calibrated_spectra(reader, search_range=10e-3, calib_snr_threshold=4, calibrants_mz=targets, suppress_warnings=True)
    
    import logging
    logging.basicConfig(level=logging.INFO)
    axs = spec.set_targets(
        [mC37_2, mC37_3],
        method_peak_center='theory',  # take intensity at theorethical positions
        method='max',
        reader=reader,
        plts=plts, suppress_warnings=True
    )
    logging.basicConfig(level=logging.WARNING)
    axs[1].vlines(targets, 0, 2e7)
    plt.show()

    with_calib = spec.feature_table.mean()


# test_small_example(True)

def calibration_for_targets():
    folder = r'C:\Users\Yannick Zander\Downloads\maspim workshop\data\small example'
    p = get_project(True, folder)
    reader = p.require_hdf_reader()
    p.set_spectra(reader=reader, full=False)
    spec = p.spectra
    
    targets = [mC37_2, mC37_3]
    
    spec.add_all_spectra(reader)
    spec.subtract_baseline()
    spec.set_peaks(1e7)
    ax = spec.plot_peaks()
    
    calib_window = 30e-3
    spec.add_calibrated_spectra(reader, search_range=calib_window, calib_snr_threshold=0, min_height=0, max_degree=0, calibrants_mz=targets)
    spec.set_peaks(1e7)
    ax = spec.plot_peaks(ax)
    ax.vlines(targets, 0, spec.intensities.max(), colors='red')
    
    calibrants = spec._calibration_settings['calibrants']
    ax.vlines(calibrants, 0, spec.intensities.max(), colors='black')
    for cal in calibrants:
        ax.fill_betweenx([0, spec.intensities.max()], cal - calib_window / 2, cal + calib_window / 2, alpha=.5, color='red')
    plt.show()


def plot_individual_calibrations():
    # plot invdividual spectra before and after calibration
    folder = r'C:\Users\Yannick Zander\Downloads\maspim workshop\data\small example'
    p = get_project(True, folder)
    reader = p.require_hdf_reader()
    p.set_spectra(reader=reader, full=False)
    spec = p.spectra

    targets = [mC37_2, mC37_3]

    spec.add_calibrated_spectra(reader, search_range=10e-3, calib_snr_threshold=0, min_height=0, max_degree=0, calibrants_mz=targets)
    spec.set_peaks(1e7)

    sspec_c = np.zeros_like(spec.mzs)
    sspec = np.zeros_like(spec.mzs)
    plt.figure()
    for i in range(72):
        spec_ = reader.get_spectrum(i + 1)
        spec_c = reader.get_spectrum(i + 1, poly_coeffs=spec._calibration_parameters[i])
        spec_c.resample(spec.mzs)
        y = spec_.intensities / spec_.intensities.max()
        yc = spec_c.intensities / spec_c.intensities.max()

        plt.plot(y + i, c='blue', alpha=.5)
        plt.plot(yc + i, c='red', alpha=.5)
        sspec_c += yc
        sspec += y
    # peaks = np.zeros(spec.mzs.shape[0])
    # peaks[spec._peaks] = 72
    # plt.stem(peaks, markerfmt='', linefmt='black')
    plt.vlines([np.argmin(np.abs(t - spec.mzs)) for t in targets], 0, 72, colors='black')
    plt.plot(sspec, c='lightblue')
    plt.plot(sspec_c, c='orange')
    plt.show()

test_small_example(True)

# axs = spec.set_targets(
#     [mC37_2, mC37_3],
#     tolerances=10e-3,
#     method_peak_center='closest',  # take intensity at theorethical positions
#     method='height',
#     reader=reader,
#     plts=True
# )
# plt.show()

# spec.plot_peaks()
# plt.show()


# ax = test_synthetic_offset(shift=-4e-3)
# ax.set_xlim([551.25, 551.75])
# plt.show()

# for i in range(1, 72):
#     _spec = spec.get_spectrum(reader, i + 1, False)
    
#     polycoeffs, n_coeffs, calibs_found = calibrate_spectrum(
#         mzs=_spec.mzs,
#         intensities=_spec.intensities,
#         calibrants_mz=cbr_mzs,
#         search_range=5e-3,
#         calib_snr_threshold=4,
#         noise_level=spec.noise_level,
#         min_height=10000,
#         nearest=False,
#         max_degree=1)
    
#     plot_calibration(_spec, polycoeffs, cbr_mzs[calibs_found])
    
    
# # %%
# _spec = spec.get_spectrum(reader, 7, False)

# _spec.mzs += 4e-3

# polycoeffs, n_coeffs, calibs_found = find_polycalibration_spectrum(
#     mzs=_spec.mzs,
#     intensities=_spec.intensities,
#     calibrants_mz=cbr_mzs,
#     search_range=5e-3,
#     calib_snr_threshold=4,
#     noise_level=spec.noise_level,
#     min_height=10000,
#     nearest=False,
#     max_degree=1)
#
# plot_calibration(_spec, polycoeffs, cbr_mzs[calibs_found])
