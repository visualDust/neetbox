from thop import profile as _profile
from neetbox.core import *
import time
from tqdm import tqdm
import torch

logger = get_static_logger()

def profile(model, input_shape=(1,3,2048,1024), profiling = True, speedtest = 1000):
    tensor = torch.rand(input_shape) # creating input tensor
    if next(model.parameters()).is_cuda:
        tensor = tensor.cuda()
    if speedtest:
        counter = []
        logger.log("running LatencyTest...")
        model.eval()
        with torch.no_grad():
            logger.log("start warm up")
            for i in tqdm(range(10)):
                model(tensor)
            logger.log("warm up done")
            logger.log("calculating FPS...")
            for test_index in tqdm(range(speedtest+2)):
                t = time.time()
                model(tensor)
                counter.append(time.time() - t)
            _min, _max, _sum = min(counter), max(counter), sum(counter)
            aver = (_sum - _min - _max) / (len(counter) - 2)
            logger.log(f"speedTest: average {aver}s per run with input size {input_shape}")
            logger.log(f"min inference time: {_min}s, Max inference time: {_max}")
            logger.log(f"FPS: {speedtest / _sum} per second")
        
    if profiling:
        logger.log("model profiling...")
        tensor = torch.rand(input_shape)
        if next(model.parameters()).is_cuda:
            tensor = tensor.cuda()
        tensor = (tensor,)
        flops, params = _profile(model, inputs=tensor)
        logger.log(f"Model FLOPs = {flops/1e9}, params = {params/1e6}")