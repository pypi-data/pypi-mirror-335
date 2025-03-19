import os

from maspim import get_project
from .parameters import (path_msi_folder, path_xrf_folder, params_msi,
                         params_xrf, path_test_folder, params_test,
                         params_artificial, path_artificial_folder)


def test_set_files_msi():
    project = get_project(is_MSI=True,
                          path_folder=os.path.join(path_artificial_folder, 'MSI'),
                          d_folder=params_artificial['d_folder'])

    # set files
    assert project.d_folder == params_artificial['d_folder']
    assert project.mis_file == params_artificial['mis_file']
    msi_files = [
        'peaks_file',
        'Spectra_file',
        'MSI_file',
        'AgeModel_file',
        'TimeSeries_file',
        'ImageSample_file',
        'ImageROI_file',
        'ImageClassified_file',
        'SampleImageHandlerMSI_file',
        'DataAnalysisExport_file',
        'hdf_file',
        'XRayROI_file'
    ]
    for file in msi_files:
        assert hasattr(project, file), f'was expecting to find {file}'


def test_set_xrf_files():
    project = get_project(is_MSI=False, path_folder=path_xrf_folder)

    assert os.path.samefile(project.path_bcf_file, params_xrf['path_bcf_file'])
    # this test is annoying since there are also the D files
    # assert os.path.samefile(project.path_image_file, params_xrf['path_image_file'])
    # assert os.path.samefile(project.path_image_roi_file, params_xrf['path_image_roi_file'])


