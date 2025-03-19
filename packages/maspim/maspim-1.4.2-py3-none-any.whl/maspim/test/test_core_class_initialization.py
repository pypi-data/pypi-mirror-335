import os
import unittest
import numpy as np


def test_project_msi(depth_span=(490, 495)):
    from maspim import get_project
    from .parameters import path_msi_folder, path_artificial_folder

    project = get_project(is_MSI=True, path_folder=path_msi_folder)
    assert project._is_MSI
    assert project._is_laminated
    assert not project._corrected_tilt

    project = get_project(is_MSI=True, path_folder=path_msi_folder, is_laminated=True)
    assert project._is_laminated
    project = get_project(is_MSI=True, path_folder=path_msi_folder, is_laminated=False)
    assert not project._is_laminated

    project = get_project(is_MSI=True, path_folder=path_msi_folder, depth_span=depth_span)
    assert project.depth_span == depth_span

    # non-existing mis file will not raise Error
    project = get_project(is_MSI=True, path_folder=path_msi_folder, mis_file='test.mis')
    assert project.mis_file == 'test.mis'

    # two d folders, should result in error
    tc = unittest.TestCase()
    with tc.assertRaises(AssertionError):
        get_project(is_MSI=True, path_folder=path_artificial_folder)
    project = get_project(is_MSI=True,
                          path_folder=os.path.join(path_artificial_folder, 'MSI'),
                          d_folder='test.d')
    assert project.d_folder == 'test.d'
    project = get_project(is_MSI=True,
                          path_folder=os.path.join(path_artificial_folder, 'MSI'),
                          d_folder='data.d')
    assert project.d_folder == 'data.d'


def test_project_xrf():
    from maspim import get_project
    from .parameters import path_xrf_folder, params_xrf

    project = get_project(is_MSI=False, path_folder=path_xrf_folder)
    assert project.measurement_name == params_xrf['measurement_name']
    assert not project._is_MSI
    assert project._is_laminated
    assert not project._corrected_tilt


def test_sample_image_handler_msi():
    from maspim import get_project, SampleImageHandlerMSI
    from .parameters import path_msi_folder, params_msi

    # init through folder
    handler = SampleImageHandlerMSI(path_folder=path_msi_folder)
    assert handler.d_folder == params_msi['d_folder']
    assert handler.mis_file == params_msi['mis_file']
    assert handler.image_file == params_msi['img_file']

    # try:
    #     project = get_project(is_MSI=True, path_folder=path_msi_folder)
    #     project.set_image_handler()
    # except Exception as e:
    #     raise AssertionError(e)


def test_sample_image_handler_xrf():
    from maspim import get_project, SampleImageHandlerXRF
    from .parameters import path_xrf_folder, params_xrf

    # init through folder
    SampleImageHandlerXRF(path_folder=path_xrf_folder)
    # init through image file and roi file
    handler = SampleImageHandlerXRF(path_image_file=params_xrf['path_image_file'],
                                    path_image_roi_file=params_xrf['path_image_roi_file'])
    assert os.path.samefile(handler.path_image_file, params_xrf['path_image_file'])
    assert os.path.samefile(handler.path_image_roi_file, params_xrf['path_image_roi_file'])

    # assuming roi is same as image if not provided
    handler = SampleImageHandlerXRF(path_image_file=params_xrf['path_image_file'])
    assert handler.image_file == handler.image_roi_file

    # try:
    #     project = get_project(is_MSI=False, path_folder=path_xrf_folder)
    #     project.set_image_handler()
    # except Exception as e:
    #     raise AssertionError(e)


def test_imaging_info_xml():
    from maspim import ImagingInfoXML
    from .parameters import path_msi_folder, params_msi

    # can be initialized from folder, d_folder or file
    try:
        info = ImagingInfoXML(path_folder=path_msi_folder)
        assert os.path.samefile(info.path_file, params_msi['path_file_imaging_info'])
    except Exception as e:
        AttributeError(e)

    try:
        info = ImagingInfoXML(path_d_folder=os.path.join(path_msi_folder, params_msi['d_folder']))
        assert os.path.samefile(info.path_file, params_msi['path_file_imaging_info'])
    except Exception as e:
        AttributeError(e)

    try:
        info = ImagingInfoXML(path_file=params_msi['path_imaging_info_file'])
        assert os.path.samefile(info.path_file, params_msi['path_file_imaging_info'])
    except Exception as e:
        AttributeError(e)


def test_xray():
    from maspim import XRay
    from .parameters import path_xray_folder, params_xray

    # can be initialized using path_folder or path_image_file
    xray = XRay.from_disk(path_folder=path_xray_folder)
    assert not xray._bars_removed
    assert xray._use_rotated
    assert xray.depth_section is None

    xray = XRay(path_image_file=os.path.join(path_xray_folder, params_xray['image_file']))
    assert not xray._bars_removed
    assert xray._use_rotated
    assert xray.depth_section is None


def test_transformation():
    from maspim import Transformation, ImageROI

    # can either provide np arrays and color or ImageROI
    s = np.ones((3, 3))
    t = np.eye(3)
    Transformation(source=s, target=t, source_obj_color='light', target_obj_color='dark')

    s = ImageROI(image=s, obj_color='light')
    t = ImageROI(image=t, obj_color='dark')
    Transformation(source=s, target=t, source_obj_color='light', target_obj_color='dark')


def test_descriptor():
    from maspim import Descriptor

    image = np.ones((100, 100))
    d = Descriptor(image=image)
    assert d.max_period == 10
    assert d.min_period == 5  # get's capped at 5
    assert d.kernel_type == 'rect'
    assert np.allclose(d.image, image)
    assert np.all(d.mask)
    assert d.n_angles == 32
    assert d.n_sizes == 8
    assert d.n_phases == 8
    assert d.nx == np.ceil(10 * np.sqrt(2)).astype(int)

    assert d.widths.min() == d.min_period
    assert d.widths.max() == d.max_period
    assert d.angles.min() == 0
    assert d.angles.max() < 2 * np.pi
    assert d.phases.min() == 0
    assert d.phases.max() < 2 * np.pi

    assert len(d.phases) == d.n_phases
    assert len(d.angles) == d.n_angles
    assert len(d.widths) == d.n_sizes


def test_image_sample():
    from maspim import ImageSample
    from .parameters import params_xrf, path_msi_folder

    # either image or path_image_file
    ImageSample(image=np.ones((3, 3)))
    ImageSample(path_image_file=params_xrf['path_image_file'])
    ImageSample.from_disk(path_msi_folder)


def test_image_roi():
    from maspim import ImageROI, ImageSample
    from .parameters import params_xrf, path_msi_folder

    # either image or path_image_file and obj_color
    obj_color = 'light'
    ImageROI(image=np.ones((3, 3)), obj_color=obj_color)
    ImageROI(path_image_file=params_xrf['path_image_file'], obj_color=obj_color)
    ImageROI.from_disk(path_msi_folder)

    ImageROI.from_parent(ImageSample.from_disk(path_msi_folder))


def test_image_classified():
    from maspim import ImageROI, ImageSample
    from .parameters import params_xrf, path_msi_folder

    # either image or path_image_file and obj_color
    obj_color = 'light'
    ImageROI(image=np.ones((3, 3)), obj_color=obj_color)
    ImageROI(path_image_file=params_xrf['path_image_file'], obj_color=obj_color)
    ImageROI.from_disk(path_msi_folder)

    ImageROI.from_parent(ImageSample.from_disk(path_msi_folder))


def test_read_bruker_mcf():
    from maspim import ReadBrukerMCF
    from .parameters import path_test_folder, params_test

    mcf = ReadBrukerMCF(path_d_folder=os.path.join(path_test_folder, params_test['d_folder']))


def test_hdf5_handler():
    from maspim import hdf5Handler
    from .parameters import path_test_folder, params_test

    # can provide hdf5 or d folder
    handler = hdf5Handler(path_file=os.path.join(path_test_folder,
                                                 params_test['d_folder']))
    assert handler.file == 'Spectra.hdf5'
    assert handler.d_folder == params_test['d_folder']
    assert os.path.samefile(handler.path_folder, path_test_folder)

    handler = hdf5Handler(path_file=os.path.join(path_test_folder,
                                                 params_test['d_folder'],
                                                 'Spectra.hdf5'))
    assert handler.file == 'Spectra.hdf5'
    assert handler.d_folder == params_test['d_folder']
    assert os.path.samefile(handler.path_folder, path_test_folder)


def test_data_analysis_export():
    from maspim import DataAnalysisExport
    from .parameters import params_msi, path_msi_folder

    da = DataAnalysisExport(path_file=params_msi['da_export_file'])
    assert da.path_file == params_msi['da_export_file']
    assert os.path.samefile(da.path_folder, os.path.join(path_msi_folder, 'DataAnalysis export'))
    assert da._peak_th == .1
    assert da._normalization == 'None'


def test_spectra():
    from maspim import Spectra, hdf5Handler
    from .parameters import path_msi_folder, params_msi

    # either reader or ininiate=False and d-folder
    hdf = hdf5Handler(path_file=os.path.join(path_msi_folder, params_msi['d_folder'], 'Spectra.hdf5'))
    Spectra(reader=hdf)

    Spectra(path_d_folder=os.path.join(path_msi_folder, params_msi['d_folder']), initiate=False)


def test_age_model():
    from maspim import AgeModel
    from .parameters import notebook_age_model

    # provide either age and depth or file
    am = AgeModel(age=[1, 2, 3], depth=[0, 1, 3])
    assert am._save_file is None
    assert am.path_folder is None
    assert am._in_file is None
    assert am.column_depth == 'depth'
    assert am.column_age == 'age'

    # from file
    am = AgeModel(path_file=notebook_age_model, sep='\t', skiprows=15)
    assert am._save_file == 'AgeModel.pickle'
    assert os.path.samefile(am.path_folder, os.path.dirname(notebook_age_model))
    assert am._in_file == os.path.basename(notebook_age_model)
    assert am.column_depth == 'Depth sed [m]'
    assert am.column_age == 'Age model [ka]'
    # TODO: from save
    ...


def test_msi():
    from maspim import MSI
    from .parameters import path_msi_folder, params_msi

    # provide d folder
    msi = MSI(path_d_folder=os.path.join(path_msi_folder, params_msi['d_folder']))
    assert os.path.samefile(path_msi_folder, msi.path_folder)
    assert msi.d_folder == params_msi['d_folder']
    assert msi._distance_pixels is None
    assert msi.mis_file is None

    # from spectra
    ...
    # msi.inject_feature_table_from(spectra)


def test_xrf():
    from maspim import XRF
    from .parameters import path_xrf_folder, params_xrf

    xrf = XRF(path_folder=path_xrf_folder)
    assert xrf._distance_pixels is None
    assert xrf.measurement_name == params_xrf['measurement_name']







