import torch
import torch.nn as nn
import torch.nn.functional as F


def ConvNxN(inplanes, outplanes, kernel_size=3, stride=1, padding=True, dilation=1):
    padding_size = (kernel_size // 2) * dilation if padding else 0
    return nn.Conv2d(
        in_channels=inplanes,
        out_channels=outplanes,
        kernel_size=kernel_size,
        padding=(padding_size, padding_size),
        stride=stride,
        dilation=dilation,
    )


def SpatialSeparableConvNxN(planes, kernel_size, dilation=1):
    padding_size = (kernel_size // 2) * dilation
    return nn.Sequential(
        nn.Conv2d(
            in_channels=planes,
            out_channels=planes,
            kernel_size=(kernel_size, 1),
            padding=(padding_size, 0),
            stride=1,
            dilation=dilation,
        ),
        nn.Conv2d(
            in_channels=planes,
            out_channels=planes,
            kernel_size=(1, kernel_size),
            padding=(0, padding_size),
            stride=1,
            dilation=dilation,
        ),
    )


class ConvNxN_Bn(nn.Module):
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
        pool_on_residual_downsample=False,
        bn_momentum=0.1,
        skip_last_relu=False,
    ):
        super(ConvNxN_Bn, self).__init__()
        padding_size = kernel_size // 2 if padding else 0
        self.conv1 = ConvNxN(
            inplanes=inplanes,
            outplanes=outplanes,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
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
            )
        else:
            self.conv2 = SpatialSeparableConvNxN(
                planes=outplanes, kernel_size=kernel_size, dilation=dilation
            )
        self.bn2 = nn.BatchNorm2d(num_features=outplanes, momentum=bn_momentum)
        self.residual = None
        if residual:
            if pool_on_residual_downsample:
                assert pool_on_residual_downsample in ["maxpool", "averagepool"]
                if pool_on_residual_downsample == "maxpool":
                    self.residual = nn.MaxPool2d(
                        kernel_size=kernel_size, stride=stride, padding=padding_size
                    )
                elif pool_on_residual_downsample == "averagepool":
                    self.residual = nn.AvgPool2d(
                        kernel_size=kernel_size, stride=stride, padding=padding_size
                    )
            else:
                self.residual = nn.Sequential(
                    ConvNxN(
                        inplanes=inplanes,
                        outplanes=outplanes,
                        kernel_size=1,
                        stride=stride,
                        padding=padding,
                        dilation=dilation,
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
