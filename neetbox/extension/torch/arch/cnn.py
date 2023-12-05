# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

import torch.nn as nn


def ConvNxN(
    inplanes,
    outplanes,
    kernel_size=3,
    stride=1,
    padding=True,
    dilation=1,
    depthwise=False,
):
    """ConvNxN

    Args:
        inplanes (int): num of channel input
        outplanes (int): num of channel output
        kernel_size (int, optional): kernel size. Defaults to 3.
        stride (int, optional): stride. Defaults to 1.
        padding (bool, optional): padding. Defaults to True.
        dilation (int, optional): dilation rate. Defaults to 1.

    Returns:
        nn.Conv2d: the convolution layer
    """
    if depthwise:
        assert outplanes % inplanes == 0
    padding_size = (kernel_size // 2) * dilation if padding else 0
    return nn.Conv2d(
        in_channels=inplanes,
        out_channels=outplanes,
        kernel_size=kernel_size,
        padding=(padding_size, padding_size),
        stride=stride,
        dilation=dilation,
        groups=1 if not depthwise else inplanes,
    )


def SpatialSeparableConvNxN(planes, kernel_size=3, padding=True, dilation=1, depthwise=False):
    """SpatialSeparableConvNxN

    Args:
        planes (int): num of channel input and output
        kernel_size (int, optional): kernel size. Defaults to 3.
        dilation (int, optional): dilation rate. Defaults to 1.

    Returns:
        _type_: _description_
    """
    padding_size = (kernel_size // 2) * dilation if padding else 0
    return nn.Sequential(
        nn.Conv2d(
            in_channels=planes,
            out_channels=planes,
            kernel_size=(kernel_size, 1),
            padding=(padding_size, 0),
            stride=1,
            dilation=dilation,
            groups=1 if not depthwise else planes,
        ),
        nn.Conv2d(
            in_channels=planes,
            out_channels=planes,
            kernel_size=(1, kernel_size),
            padding=(0, padding_size),
            stride=1,
            dilation=dilation,
            groups=1 if not depthwise else planes,
        ),
    )


class ResBlock(nn.Module):
    def __init__(
        self,
        inplanes,
        outplanes,
        kernel_size=3,
        stride=1,
        padding=True,
        residual=False,
        spatial_separable=False,
        dilation=1,
        depthwise=False,
        pool_on_residual_downsample=False,
        bn_momentum=0.1,
        skip_last_relu=False,
    ):
        """ResBlock

        Args:
            inplanes (int): num of channel input
            outplanes (int): num of channel output
            kernel_size (int, optional): kernel size. Defaults to 3.
            stride (int, optional): stride for downsampling layer. Defaults to 1.
            padding (bool, optional): decide if use padding. Defaults to True.
            residual (bool, optional): wether use residual. Defaults to False.
            spatial_separable (bool, optional): set spatial separable for non-downsamping layers. Defaults to False.
            dilation (int, optional): dilation rate. Defaults to 1.
            depthwise (bool, optional): wether to use depthwise convolution. Defaults to False.
            pool_on_residual_downsample (bool, optional): 'maxpool' or 'averagepool' if you want to use pooling instead of conv2d on residual path. Defaults to False.
            bn_momentum (float, optional): momentum of batch norms. Defaults to 0.1.
            skip_last_relu (bool, optional): wether to skip the last relu. Defaults to False.
        """
        super(ResBlock, self).__init__()
        residual_padding_size = kernel_size // 2 if padding else 0
        self.conv1 = ConvNxN(
            inplanes=inplanes,
            outplanes=outplanes,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            depthwise=depthwise,
        )
        self.bn1 = nn.BatchNorm2d(num_features=outplanes, momentum=bn_momentum)
        self.relu_inplace = nn.ReLU(inplace=True)
        if not spatial_separable:
            self.conv2 = ConvNxN(
                inplanes=outplanes,
                outplanes=outplanes,
                kernel_size=kernel_size,
                stride=1,
                padding=padding,
                dilation=dilation,
                depthwise=depthwise,
            )
        else:
            self.conv2 = SpatialSeparableConvNxN(
                planes=outplanes,
                kernel_size=kernel_size,
                dilation=dilation,
                depthwise=depthwise,
            )
        self.bn2 = nn.BatchNorm2d(num_features=outplanes, momentum=bn_momentum)
        self.residual = None
        if residual:
            if pool_on_residual_downsample:
                assert inplanes == outplanes
                assert pool_on_residual_downsample in ["maxpool", "averagepool"]
                if pool_on_residual_downsample == "maxpool":
                    self.residual = nn.MaxPool2d(
                        kernel_size=kernel_size,
                        stride=stride,
                        padding=residual_padding_size,
                    )
                elif pool_on_residual_downsample == "averagepool":
                    self.residual = nn.AvgPool2d(
                        kernel_size=kernel_size,
                        stride=stride,
                        padding=residual_padding_size,
                    )
            else:
                self.residual = nn.Sequential(
                    ConvNxN(
                        inplanes=inplanes,
                        outplanes=outplanes,
                        kernel_size=1,
                        stride=stride,
                    ),
                    nn.BatchNorm2d(num_features=outplanes, momentum=bn_momentum),
                )
        self.skip_last_relu = skip_last_relu

    def forward(self, x):
        _x = self.conv1(x)
        _x = self.bn1(_x)
        _x = self.relu_inplace(_x)
        _x = self.conv2(_x)
        _x = self.bn2(_x)
        if self.residual:
            _x_res = self.residual(x)
            _x = _x + _x_res
        if not self.skip_last_relu:
            _x = self.relu_inplace(_x)
        return _x


class InceptionBlock(nn.Module):
    def __init__(self, **kwargs) -> None:
        super(InceptionBlock, self).__init__()
