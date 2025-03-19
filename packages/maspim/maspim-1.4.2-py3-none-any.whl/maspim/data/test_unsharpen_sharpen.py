import numpy as np
import matplotlib.pyplot as plt
import skimage

from skimage.transform import warp
from skimage.filters import gaussian
from skimage.restoration import unsupervised_wiener, wiener
from scipy.ndimage._filters import _gaussian_kernel1d
from numpy.fft import fft2 as fft
from numpy.fft import ifft2 as ifft
from scipy.signal import fftconvolve

np.random.seed(1)

image = skimage.data.cat()[:, :, 0]
image_shape = image.shape
# image_shape = (50, 300)
# image = np.random.random(image_shape) * 255
# image[image < 220] = 0

# image = image.astype(float) / image.max()

deformation_x = ((np.random.random(image_shape)) - .5) / 2
deformation_x = np.cumsum(deformation_x, axis=0)
deformation_x = np.cumsum(deformation_x, axis=1)

deformation_x = gaussian(deformation_x, sigma=2)
deformation_x = gaussian(deformation_x, sigma=2)
deformation_x = gaussian(deformation_x, sigma=2)
deformation_x = gaussian(deformation_x, sigma=2)
deformation_x = gaussian(deformation_x, sigma=2)

deformation_y = ((np.random.random(image_shape)) - .5) / 2
deformation_y = np.cumsum(deformation_y, axis=0)
deformation_y = np.cumsum(deformation_y, axis=1)

deformation_y = gaussian(deformation_y, sigma=2)
deformation_y = gaussian(deformation_y, sigma=2)
deformation_y = gaussian(deformation_y, sigma=2)
deformation_y = gaussian(deformation_y, sigma=2)
deformation_y = gaussian(deformation_y, sigma=2)

V, U = np.indices(image_shape)

warped = warp(image,
              np.array([deformation_y + V, deformation_x + U]),
              mode='edge',
              preserve_range=True)

bins = np.linspace(0., image.max(), round(np.sqrt(image.shape[0] * image.shape[1])))[1:]


# %% not smoothing
print('plotting...')
fig, axs = plt.subplots(ncols=2, nrows=3)
axs[0, 0].imshow(deformation_x)
axs[0, 0].set_title(r'$\Delta x$')
axs[0, 1].imshow(deformation_y)
axs[0, 1].set_title(r'$\Delta y$')

axs[1, 0].imshow(image)
axs[1, 0].set_title(r'Original')

axs[1, 1].hist(image.ravel(), bins=bins)
print('first row done')
axs[2, 0].imshow(warped)
axs[2, 0].set_title(r'Warped')

axs[2, 1].hist(warped.ravel(), bins=bins)
print('second row done')
plt.show()

print(image.sum(), warped.sum())

# %% unsharpen-sharpen

sigma = 5
truncate = 4
radius = int(truncate * sigma + 0.5)

gauss_x = _gaussian_kernel1d(sigma, order=0, radius=radius)[::-1]
gauss_y = _gaussian_kernel1d(sigma, order=0, radius=radius)[::-1]
h = gauss_x[None, :] * gauss_y[:, None]
# h = np.ones((5, 5)) / 25

# smoothed = gaussian(image, sigma=sigma, truncate=truncate)
# from scipy.signal import convolve2d
# smoothed = convolve2d(image, h, mode='same')
smoothed = fftconvolve(image, h, mode='same')

smoothed_warped = warp(smoothed,
                       np.array([deformation_y + V, deformation_x + U]),
                       mode='edge',
                       preserve_range=True)

ft_original = fft(smoothed)
ft_smooth_warped = fft(smoothed_warped)
ft_h = fft(h, s=image_shape) + 1e-8

sharpend_warped = ifft(ft_smooth_warped / ft_h)
sharpened_original = ifft(ft_original / ft_h)

fig, axs = plt.subplots(ncols=2, nrows=3, sharex='col', sharey='row')

axs[0, 0].imshow(smoothed)
axs[0, 0].set_title('smoothed')

axs[0, 1].imshow(smoothed_warped)
axs[0, 1].set_title('smoothed warped')

axs[1, 0].imshow(np.abs(ft_original))
axs[1, 0].set_title('FT')

axs[1, 1].imshow(np.abs(ft_smooth_warped))
axs[1, 1].set_title('FT warped')

axs[2, 0].imshow(np.real(sharpened_original))
axs[2, 0].set_title('sharpened')

axs[2, 1].imshow(np.real(sharpend_warped))
axs[2, 1].set_title('sharpened warped')

plt.show()

# %% wiener

balance = 1e-12
restored = wiener(smoothed, h, is_real=False, balance=balance)
restored_warped = wiener(smoothed_warped, h, is_real=False, balance=balance)

fig, axs = plt.subplots(ncols=2, nrows=2, sharex='col', sharey='row')

axs[0, 0].imshow(smoothed)
axs[0, 0].set_title('smoothed')

axs[0, 1].imshow(smoothed_warped)
axs[0, 1].set_title('smoothed warped')

axs[1, 0].imshow(np.abs(restored))
axs[1, 0].set_title('restored')

axs[1, 1].imshow(np.abs(restored_warped))
axs[1, 1].set_title('restored warped')

plt.show()

# %% richardson lucy
smoothed = fftconvolve(image, h, mode='full')

smoothed_warped = warp(smoothed,
                       np.array([deformation_y + V, deformation_x + U]),
                       mode='edge',
                       preserve_range=True)

mask = np.index_exp[h.shape[0] // 2:-h.shape[0] // 2, h.shape[1] // 2:-h.shape[1] // 2]
sharpened = skimage.restoration.richardson_lucy(smoothed, h, 100, clip=False)[mask]
sharpened_warped = skimage.restoration.richardson_lucy(smoothed_warped, h, 100, clip=False)[mask]

plt.imshow(sharpened)
plt.show()

plt.imshow(sharpened_warped)
plt.show()

# %% up- and downscale


def downscale_cells_median(image, cell_size: int):
    assert image.ndim == 2, 'must be 2D image'
    assert image.shape[0] % cell_size == 0, \
        'image dimensions must be multiple of cell size'
    assert image.shape[1] % cell_size == 0, \
        'image dimensions must be multiple of cell size'
    
    h_new = image.shape[0] // cell_size
    w_new = image.shape[1] // cell_size
    image_downscaled = np.zeros((h_new, w_new), dtype=image.dtype)
    
    for i in range(h_new):
        for j in range(w_new):
            image_downscaled[i, j] = np.median(
                image[i * cell_size:(i + 1) * cell_size, 
                      j * cell_size:(j + 1) * cell_size]
            )
    return image_downscaled


def upscale_cells(image, cell_size: int):
    assert image.ndim == 2, 'must be 2D image'
        
    h, w = image.shape
    image_upscaled = np.zeros((h * cell_size, w * cell_size), dtype=image.dtype)
    
    for i in range(h):
        for j in range(w):
            cell_idcs = np.index_exp[i * cell_size:(i + 1) * cell_size, 
                                     j * cell_size:(j + 1) * cell_size]
            image_upscaled[cell_idcs] = image[i, j]
    return image_upscaled


# upscale 
scale_factor = 16

image_upscaled = skimage.transform.rescale(image, 
                                            scale_factor, 
                                            preserve_range=True, 
                                            order=0)  # closest
# image_upscaled = upscale_cells(image, cell_size=scale_factor)
V_upscaled = skimage.transform.rescale((deformation_y + V) * scale_factor, 
                                        scale_factor, 
                                        preserve_range=True, 
                                        order=1)
U_upscaled = skimage.transform.rescale((deformation_x + U) * scale_factor, 
                                        scale_factor, 
                                        preserve_range=True, 
                                        order=1)

warped_upscaled = warp(image_upscaled,
                       np.array([V_upscaled, 
                                 U_upscaled]),
                       mode='edge',
                       preserve_range=True)

# restore values
# import maspim
# uvals = np.unique(image)
# warped_upscaled_unique = maspim.imaging.util.image_helpers.restore_unique_values(warped_upscaled, uvals)

# in each 16 x 16 cell, choose the median value
# warped = skimage.transform.downscale_local_mean(warped_upscaled, scale_factor)
warped = downscale_cells_median(warped_upscaled, cell_size=scale_factor)

# thr low vals
# smallest_nonzero = np.unique(image)[1]
# warped[warped < smallest_nonzero] = 0

fig, axs = plt.subplots(ncols=2, nrows=4)

axs[0, 0].imshow(image)
axs[0, 0].set_title(r'Original')
axs[0, 1].hist(image.ravel(), bins=bins)

axs[1, 0].imshow(image_upscaled)
axs[1, 0].set_title(r'upscaled')
axs[1, 1].hist(image_upscaled.ravel(), bins=bins)

axs[2, 0].imshow(warped_upscaled)
axs[2, 0].set_title(r'Warped upscaled')
axs[2, 1].hist(warped_upscaled.ravel(), bins=bins)

# axs[3, 0].imshow(warped_upscaled)
# axs[3, 0].set_title(r'Warped restored')
# axs[3, 1].hist(warped_upscaled_unique.ravel(), bins=bins)

axs[3, 0].imshow(warped)
axs[3, 0].set_title(r'Warped')
axs[3, 1].hist(warped.ravel(), bins=bins)

plt.show()

print(image.sum(), warped.sum())

# plt.imshow(np.abs(image - warped))
# plt.show()

# %% test maspim implementation

from maspim import Mapper

mapper = Mapper(image.shape)
mapper.add_UV(U=deformation_x, V=deformation_y)

warped_mean = mapper.fit(image, preserve_range=True)
warped_median = mapper.fit(image, keep_sparse=True, scale_factor=16, threshold=False, preserve_range=True)
warped_median_sparse = mapper.fit(image, keep_sparse=True, scale_factor=16, threshold=True, preserve_range=True)

fig, axs = plt.subplots(ncols=2, nrows=4)

axs[0, 0].imshow(image)
axs[0, 0].set_title(r'Original')
axs[0, 1].hist(image.ravel(), bins=bins)

axs[1, 0].imshow(warped_mean)
axs[1, 0].set_title(r'warped')
axs[1, 1].hist(warped_mean.ravel(), bins=bins)

axs[2, 0].imshow(warped_median)
axs[2, 0].set_title(r'Warped with upscaling')
axs[2, 1].hist(warped_median.ravel(), bins=bins)


axs[3, 0].imshow(warped_median_sparse)
axs[3, 0].set_title(r'Warped with upscaling and thresholding')
axs[3, 1].hist(warped_median_sparse.ravel(), bins=bins)

plt.show()
