---
sidebar_position: 2
---

# Simple Model Profiler Helper

The profiler measures your models' performance on speed and latency with given `input_shape` using your hardware.

## Get started

Import dependencies

```python
from neetbox.torch.arch import cnn
from neetbox.torch.profile import profile
```

Build a basic network:
```python
model = cnn.ResBlock(
    inplanes=64, outplanes=128, kernel_size=3, stride=2, residual=True, dilation=2
).cuda()
model.eval()
```
output:
```
ResBlock(
  (conv1): Conv2d(64, 128, kernel_size=(3, 3), stride=(2, 2), padding=(2, 2), dilation=(2, 2))
  (bn1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
  (relu_inplace): ReLU(inplace=True)
  (conv2): Conv2d(128, 128, kernel_size=(3, 3), stride=(1, 1), padding=(2, 2), dilation=(2, 2))
  (bn2): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
  (residual): Sequential(
    (0): Conv2d(64, 128, kernel_size=(1, 1), stride=(2, 2), dilation=(2, 2))
    (1): BatchNorm2d(128, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
  )
)
```

:::tip
Anything that inherits from `torch.nn.Module` should work with `neetbox.torch.profile.profile`.
:::

Run profile:
```python
profile(model, input_shape=(1, 64, 1280, 720), speedtest=100)
```
output:
```
2023-03-15-16:49:50 > NEETBOX > running speedtest...
2023-03-15-16:49:50 > NEETBOX > start warm up
100%|██████████| 10/10 [00:03<00:00,  2.65it/s]
2023-03-15-16:49:54 > NEETBOX > warm up done
100%|██████████| 102/102 [00:00<00:00, 133.97it/s]
2023-03-15-16:49:55 > NEETBOX > average 0.007300891876220703s per run with out put size torch.Size([1, 128, 640, 360])
2023-03-15-16:49:55 > NEETBOX > min inference time: 0.0s, Max inference time: 0.030241966247558594s
2023-03-15-16:49:55 > NEETBOX > That is 136.96956713700143 frames per second
2023-03-15-16:49:55 > NEETBOX > ====================================================
2023-03-15-16:49:55 > NEETBOX > running CUDA side synchronous speedtest...
100%|██████████| 102/102 [00:02<00:00, 39.46it/s]
2023-03-15-16:49:58 > NEETBOX > average 0.015801547095179558s per run with out put size torch.Size([1, 128, 640, 360])
2023-03-15-16:49:58 > NEETBOX > min inference time: 0.014497632160782814s, max inference time: 0.01753702387213707s
2023-03-15-16:49:58 > NEETBOX > That is 63.284942626953125 frames per second
[WARNING] 2023-03-15-16:49:58 > NEETBOX > Seems your model has an imbalanced performance peek on cuda side test and python side test. Consider raising speedtest loop times (currently 100 +2) to have a stable result.
[DEBUG] 2023-03-15-16:49:58 > NEETBOX > Note that the CUDA side synchronous speedtest is more reliable since you are using a GPU.
2023-03-15-16:49:58 > NEETBOX > ====================================================
2023-03-15-16:49:58 > NEETBOX > model profiling...
[INFO] Register count_convNd() for <class 'torch.nn.modules.conv.Conv2d'>.
[INFO] Register count_normalization() for <class 'torch.nn.modules.batchnorm.BatchNorm2d'>.
[INFO] Register zero_ops() for <class 'torch.nn.modules.activation.ReLU'>.
[INFO] Register zero_ops() for <class 'torch.nn.modules.container.Sequential'>.
2023-03-15-16:49:58 > NEETBOX > Model FLOPs = 53.2021248G, params = 0.230528M
```

## Read the result

The output above shows that:

- Your model runs at about 137 FPS and spends about 0.0073 seconds on average per inference without awaiting the result.
- Your model runs at about 63.28 FPS and spends about 0.0145 seconds on average per inference synchronously.
- Your model has 0.230528M parameters and runs 53.2021248 GFLOPs per inference with the given input / input size.

:::caution
If the output tells you that there is an imbalanced performance peek between CUDA side synchronous test and none-sync one, you should take the synchronous test result as the final result.
:::

## CPU or GPU

The tests run at where your model stays.

Run tests on CPU:
```python
model.cpu()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=100)
```

Run tests on GPU:
```python
model.cuda()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=100)
```

## Specify the input / input shape

You can either give an `input_shape` or specify an `specific_input`. The priority of `specific_input` is higher. If your model takes an ordinary `torch.Tensor` as input, you can both specify the `input_shape` or the `specific_input`.

For example:
```python
model.cuda()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=100)
profile(model, specific_input=torch.rand(input_shape).cuda(), speedtest=100)
```
They are the same actually.

However, if your model does not take an ordinary `torch.Tensor` as input, you should specify the `specific_input`.

:::caution
The `specific_input` should on the same device as `model` does.
:::

## Choose how `profile` actually profile

If your code looks like:
```python
model.cuda()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=100)
```
Then `profile` measures model FLOPs and params with the input of a `(1, 64, 1280, 720)` shaped Tensor, also inferences the model 100 times for speed test.

If your code looks like:
```python
model.cuda()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=False)
```
Then `profile` only measures model FLOPs and params with the input of a `(1, 64, 1280, 720)` shaped Tensor.

If your code looks like:
```python
model.cuda()
profile(model, input_shape=(1, 64, 1280, 720), speedtest=10, profiling=False)
```
Then `profile` only inferences the model 100 times for speed test with the input of a `(1, 64, 1280, 720)` shaped Tensor.
