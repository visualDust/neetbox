from thop import profile as _profile
from neetbox.logger import get_logger
import time
from tqdm import tqdm
import torch

logger = get_logger(whom="NEETBOX")

def profile(model, input_resolution=(2048,1024), profiling = True, calc_fps = 1000, speedtest = 1):
    if profiling:
        logger.log("Model profiling...")
        tensor = torch.rand(1, 3, input_resolution[1], input_resolution[0])
        if next(model.parameters()).is_cuda:
            tensor = tensor.cuda()
        tensor = (tensor,)
        flops, params = _profile(model, inputs=tensor)
        logger.log(f"Model FLOPs = {flops/1e9}, params = {params/1e6}")
    if calc_fps:
        model.eval()
        with torch.no_grad():
            tensor = torch.rand(1, 3, input_resolution[1], input_resolution[0])
            if next(model.parameters()).is_cuda:
                tensor = tensor.cuda()
            logger.log("Calculating FPS...")
            t0 = time.time()
            for _ in tqdm(range(calc_fps)):
                model(tensor)
            t1 = time.time()
            logger.log(f"FPS: {calc_fps / (t1 - t0)}")
    if speedtest:
        logger.log("Running SpeedTest...")
        logger.log("Attention that model speedtest results are different on different devices or under different circumstances.")
        model.eval()
        tensor = torch.rand(1, 3, input_resolution[1], input_resolution[0])
        if next(model.parameters()).is_cuda:
            tensor = tensor.cuda()
        _ = model(tensor)
        counter = []
        for test_index in range(speedtest+2):
            t = time.time()
            model(tensor)
            counter.append(time.time() - t)
            logger.log(f'SpeedTest: {counter[-1]:.4f}s in {test_index+1}st run.')
        if len(counter):
            _min, _max = min(counter), max(counter)
            aver = (sum(counter) - _min - _max) / (len(counter) - 2)
            logger.log(f"SpeedTest: average {aver}s per run with input size {input_resolution}")
            logger.log(f"Min inference time: {_min}s, Max inference time:{_max}")