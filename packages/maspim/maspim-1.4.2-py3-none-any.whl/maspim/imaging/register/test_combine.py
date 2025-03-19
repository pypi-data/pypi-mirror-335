import os
import maspim


def clean():
    pass


def set_msi(overwrite=False):
    project_msi.require_image_handler(plts=True, overwrite=overwrite)
    project_msi.require_image_sample(plts=True, overwrite=overwrite)
    project_msi.require_image_roi(plts=True, overwrite=overwrite)
    project_msi.require_spectra(tag='targeted', full=False)
    project_msi.require_data_object()


def set_xrf(overwrite=False):
    project_xrf.require_image_handler(plts=True, overwrite=overwrite)
    project_xrf.require_image_sample(plts=True, overwrite=overwrite)
    project_xrf.require_image_roi(plts=True, overwrite=overwrite)
    project_xrf.require_data_object()


def prepare_projects():
    project_msi.add_pixels_ROI()
    project_xrf.add_pixels_ROI()


def combine_from_bounding_box():
    prepare_projects()

    project_msi.set_punchholes(plts=True)
    project_xrf.set_punchholes(plts=True)
    
    project_msi.require_combine_mapper(
        project_xrf,
        self_tilt_correction=False,
        other_tilt_correction=False,
        mapping_method=['punchholes'],
        plts=True,
        overwrite=True, 
        is_piecewise=False,
        points_target=project_msi.holes_data,
        points_source=project_xrf.holes_data
    )
    mapper = project_msi.require_combine_mapper(project_xrf)
    project_xrf.data_object_apply_transformation(mapper, keep_sparse=False, plts=False)
    # project_msi.transform_other_data(project_xrf, use_tilt_correction=[False, False])


folder = r'C:\Users\Yannick Zander\Promotion\real test'

project_msi = maspim.get_project(True, os.path.join(folder, 'MSI'), is_laminated=True)
project_xrf = maspim.get_project(False, os.path.join(folder, 'XRF'), is_laminated=True)

project_xrf2 = maspim.get_project(False, os.path.join(folder, 'XRF'), is_laminated=True)
project_xrf2.require_data_object()

set_msi()
set_xrf()

combine_from_bounding_box()

project_xrf2.plot_comp('Al', flip=True)
project_xrf.plot_comp('Al', flip=True)
