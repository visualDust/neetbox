import pytest
pytest.skip(allow_module_level=True)

from neetbox.torch.arch import cnn
from neetbox.torch.profile import profile

model = cnn.ResBlock(
    inplanes=16,
    outplanes=32,
    kernel_size=3,
    stride=2,
    spatial_separable=True,
    residual=True,
)

model.eval()

profile(model,input_shape=(1,16,32,32))