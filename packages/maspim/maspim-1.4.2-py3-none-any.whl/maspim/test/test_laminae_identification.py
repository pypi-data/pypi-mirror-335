import os
import numpy as np
import matplotlib.pyplot as plt

from maspim import ImageSample, ImageROI, ImageClassified
from maspim.imaging.misc.fit_distorted_rectangle import find_layer, distorted_rect, animate_optimization

folder = r'C:\Users\Yannick Zander\Promotion\test laminated'
img_file = '2018_08_27 Cariaco 490-495 alkenone_0001.tif'


def set_image_classified() -> None:
    """set basic image_classified object from example image without any attrs."""
    image_sample = ImageSample(path_image_file=os.path.join(folder, img_file))

    image_roi = ImageROI.from_parent(image_sample)
    image_roi.age_span = (0, 100)

    image_classified = ImageClassified.from_parent(image_roi)
    
    image_classified.save(tag='basic')
    
    
def get_image_classified() -> ImageClassified:
    """load basic object"""
    return ImageClassified.from_disk(folder, tag='basic')


def get_phase_img(rel_width=1) -> np.ndarray:
    desc = image_classified.get_descriptor()
    from skimage.transform import resize
    
    image = -np.cos(resize(desc.image_phases, image_classified.image.shape[:2]))
    
    h = image.shape[0]
    ys = np.arange(h)
    m = np.abs(ys - h / 2) < rel_width * h / 2

    transect = image[m, :]

    return transect


def test_set_seeds():
    image_classified.set_seeds(plts=True, image=None, in_classification=True)
    image_classified.set_seeds(plts=True, image=None, in_classification=False)
        
    image_classified.set_seeds(plts=True, image=get_phase_img(.5))
    
    
# set_image_classified()

image_classified = get_image_classified()

# image_classified.set_seeds(plts=True, image=get_phase_img(.1))
image_classified.set_seeds(plts=True)

# image_classified.set_params_laminae_simplified(plts=False, fixate_height=False, degree=3, max_slope=1)

# %%
def test_layer(idx=5):
    """single layer"""
    pass 


image_classification = image_classified.image_classification

idx = 4
is_dark = False


height0 = image_classified._width_light[idx]
seed = image_classified._seeds_light[idx]

width: int = image_classification.shape[0]
half_width: int = (width + 1) // 2

image_classification_pad: np.ndarray[int] = np.pad(
    image_classification,
    ((0, 0), (half_width, half_width))
)

res, x0s = find_layer(image_classification=image_classification_pad,
                      seed=seed,
                      height0=height0,
                      fixate_height=False,
                      degree=3,
                      max_slope=.1,
                      plts=True,
                      color='light', 
                      return_steps=True, 
                      method='COBYLA')


animate_optimization(x0s, r'C:\Users\Yannick Zander\Promotion\test laminated\ani.gif', image_classification=image_classification_pad, seed=seed, is_dark=False)







