import numpy as np


def get_gaussian_kernel(k=3, mu=0, sigma=1, normalize=True):
    # compute 1 dimension gaussian
    gaussian_1D = np.linspace(-1, 1, k)
    # compute a grid distance from center
    x, y = np.meshgrid(gaussian_1D, gaussian_1D)
    distance = (x**2 + y**2) ** 0.5

    # compute the 2 dimension gaussian
    gaussian_2D = np.exp(-((distance - mu) ** 2) / (2 * sigma**2))
    gaussian_2D = gaussian_2D / (2 * np.pi * sigma**2)

    # normalize part (mathematically)
    if normalize:
        gaussian_2D = gaussian_2D / np.sum(gaussian_2D)
    return gaussian_2D


def get_sobel_kernel(k=3):
    # get range
    range = np.linspace(-(k // 2), k // 2, k)
    # compute a grid the numerator and the axis-distances
    x, y = np.meshgrid(range, range)
    sobel_2D_numerator = x
    sobel_2D_denominator = x**2 + y**2
    sobel_2D_denominator[:, k // 2] = 1  # avoid division by zero
    sobel_2D = sobel_2D_numerator / sobel_2D_denominator
    return sobel_2D


def get_thin_kernels(start=0, end=360, step=45):
    import cv2

    k_thin = 3  # actual size of the directional kernel
    # increase for a while to avoid interpolation when rotating
    k_increased = k_thin + 2

    # get 0° angle directional kernel
    thin_kernel_0 = np.zeros((k_increased, k_increased))
    thin_kernel_0[k_increased // 2, k_increased // 2] = 1
    thin_kernel_0[k_increased // 2, k_increased // 2 + 1 :] = -1

    # rotate the 0° angle directional kernel to get the other ones
    thin_kernels = []
    for angle in range(start, end, step):
        (h, w) = thin_kernel_0.shape
        # get the center to not rotate around the (0, 0) coord point
        center = (w // 2, h // 2)
        # apply rotation
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
        kernel_angle_increased = cv2.warpAffine(
            thin_kernel_0, rotation_matrix, (w, h), cv2.INTER_NEAREST
        )

        # get the k=3 kerne
        kernel_angle = kernel_angle_increased[1:-1, 1:-1]
        is_diag = abs(kernel_angle) == 1  # because of the interpolation
        kernel_angle = kernel_angle * is_diag  # because of the interpolation
        thin_kernels.append(kernel_angle)
    return thin_kernels
