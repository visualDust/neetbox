import numpy as np
import torch
import torch.nn as nn

from .kernels import *


class CannyFilter(nn.Module):
    def __init__(
        self,
        k_gaussian=3,
        mu=0,
        sigma=1,
        k_sobel=3,
        padding=True,
        use_cuda=False,
    ):
        super(CannyFilter, self).__init__()
        # device
        self.device = "cuda" if use_cuda else "cpu"
        # gaussian
        gaussian_2D = get_gaussian_kernel(k_gaussian, mu, sigma)
        # gaussian_2D = gaussian_2D[None, None, :]
        self.gaussian_filter = nn.Conv2d(
            in_channels=1,
            out_channels=1,
            kernel_size=k_gaussian,
            padding=k_gaussian // 2 if padding else 0,
            bias=False,
        )
        self.gaussian_filter.weight.data.copy_(torch.from_numpy(gaussian_2D[None, None, :]))

        # sobel
        sobel_2D = get_sobel_kernel(k_sobel)
        self.sobel_filter_x = nn.Conv2d(
            in_channels=1,
            out_channels=1,
            kernel_size=k_sobel,
            padding=k_sobel // 2 if padding else 0,
            bias=False,
        )
        self.sobel_filter_x.weight.data.copy_(torch.from_numpy(sobel_2D))

        self.sobel_filter_y = nn.Conv2d(
            in_channels=1,
            out_channels=1,
            kernel_size=k_sobel,
            padding=k_sobel // 2 if padding else 0,
            bias=False,
        )
        self.sobel_filter_y.weight.data.copy_(torch.from_numpy(sobel_2D.T))

        # thin

        thin_kernels = get_thin_kernels()
        directional_kernels = np.stack(thin_kernels)
        directional_kernels = np.expand_dims(directional_kernels, axis=1)
        self.directional_filter = nn.Conv2d(
            in_channels=1,
            out_channels=8,
            kernel_size=thin_kernels[0].shape,
            padding=thin_kernels[0].shape[-1] // 2 if padding else 0,
            bias=False,
        )
        self.directional_filter.weight.data.copy_(torch.from_numpy(directional_kernels))

        # hysteresis

        hysteresis = np.ones((3, 3)) + 0.25
        self.hysteresis = nn.Conv2d(
            in_channels=1, out_channels=1, kernel_size=3, padding=1, bias=False
        )
        self.hysteresis.weight.data.copy_(torch.from_numpy(hysteresis))
        self.hysteresis.weight.data.copy_(torch.from_numpy(hysteresis))

    @torch.no_grad()
    def forward(self, img, low_threshold=None, high_threshold=None, hysteresis=False):
        # set the setps tensors
        B, C, H, W = img.shape
        blurred = torch.zeros((B, C, H, W)).to(self.device)
        grad_x = torch.zeros((B, 1, H, W)).to(self.device)
        grad_y = torch.zeros((B, 1, H, W)).to(self.device)
        grad_magnitude = torch.zeros((B, 1, H, W)).to(self.device)
        grad_orientation = torch.zeros((B, 1, H, W)).to(self.device)

        # gaussian

        for c in range(C):
            blurred[:, c : c + 1] = self.gaussian_filter(img[:, c : c + 1])

            grad_x = grad_x + self.sobel_filter_x(blurred[:, c : c + 1])
            grad_y = grad_y + self.sobel_filter_y(blurred[:, c : c + 1])

        # thick edges

        grad_x, grad_y = grad_x / C, grad_y / C
        grad_magnitude = (grad_x**2 + grad_y**2) ** 0.5
        grad_orientation = torch.atan(grad_y / grad_x)
        grad_orientation = grad_orientation * (360 / np.pi) + 180  # convert to degree
        grad_orientation = torch.round(grad_orientation / 45) * 45  # keep a split by 45

        # thin edges

        directional = self.directional_filter(grad_magnitude)
        # get indices of positive and negative directions
        positive_idx = (grad_orientation / 45) % 8
        negative_idx = ((grad_orientation / 45) + 4) % 8
        thin_edges = grad_magnitude.clone()
        # non maximum suppression direction by direction
        for pos_i in range(4):
            neg_i = pos_i + 4
            # get the oriented grad for the angle
            is_oriented_i = (positive_idx == pos_i) * 1
            is_oriented_i = is_oriented_i + (positive_idx == neg_i) * 1
            pos_directional = directional[:, pos_i]
            neg_directional = directional[:, neg_i]
            selected_direction = torch.stack([pos_directional, neg_directional])

            # get the local maximum pixels for the angle
            is_max = selected_direction.min(dim=0)[0] > 0.0
            is_max = torch.unsqueeze(is_max, dim=1)

            # apply non-maximum suppression
            to_remove = (is_max == 0) * 1 * (is_oriented_i) > 0
            thin_edges[to_remove] = 0.0

        # thresholds

        if low_threshold is not None:
            low = thin_edges > low_threshold

            if high_threshold is not None:
                high = thin_edges > high_threshold
                # get black/gray/white only
                thin_edges = low * 0.5 + high * 0.5

                if hysteresis:
                    # get weaks and check if they are high or not
                    weak = (thin_edges == 0.5) * 1
                    weak_is_high = (self.hysteresis(thin_edges) > 1) * weak
                    thin_edges = high * 1 + weak_is_high * 1
            else:
                thin_edges = low * 1

        return blurred, grad_x, grad_y, grad_magnitude, grad_orientation, thin_edges
