from thop import profile as _profile
from neetbox.core import *
import time
from tqdm import tqdm
import torch

logger = get_static_logger()


def profile(model, input_shape=(1, 3, 2048, 1024), profiling=True, speedtest=1000):
    if speedtest:
        warmed = False
        tensor = torch.rand(input_shape)  # creating input tensor
        if next(model.parameters()).is_cuda:
            tensor = tensor.cuda()
            time_counter = torch.zeros((speedtest + 2, 1))
            time0, time1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(
                enable_timing=True
            )
            logger.log("running GPU side synchronized speed test...")
            model.eval()
            with torch.no_grad():
                logger.log("start warm up")
                output = model(tensor)
                for i in tqdm(range(10)):
                    model(tensor)
                warmed = True
                logger.log("warm up done")
                for test_index in tqdm(range(speedtest + 2)):
                    time0.record()
                    model(tensor)
                    time1.record()
                    torch.cuda.synchronize()
                    time_counter[test_index] = time0.elapsed_time(time1)
            _min, _max, _sum = (
                time_counter.min(),
                time_counter.max(),
                time_counter.sum(),
            )
            _aver = (_sum - _min - _max) / speedtest
            if type(output) is list:
                output_shape = ''
                for out in output:
                    output_shape += f'{out.shape}, '
            else: output_shape = output.shape
            logger.log(f"average {_aver / 1000.}s per run with input size {input_shape}, out put size {output_shape}")
            logger.log(f"min inference time: {_min / 1000.}s, max inference time: {_max / 1000.}s")
            logger.log(f"That is {(1. / _aver) * 1000.} frames per second")
            logger.log("====================================================")

        counter = []
        logger.log("running Latency test...")
        model.eval()
        with torch.no_grad():
            if not warmed:
                logger.log("start warm up")
                output = model(tensor)
                for i in tqdm(range(10)):
                    model(tensor)
                logger.log("warm up done")
            for test_index in tqdm(range(speedtest + 2)):
                t = time.time()
                model(tensor)
                counter.append(time.time() - t)
            _min, _max, _sum = min(counter), max(counter), sum(counter)
        _aver = (_sum - _min - _max) / speedtest
        if type(output) is list:
                output_shape = ''
                for out in output:
                    output_shape += f'{out.shape}, '
        else: output_shape = output.shape
        logger.log(f"average {_aver}s per run with input size {input_shape}, out put size {output_shape}")
        logger.log(f"min inference time: {_min}s, Max inference time: {_max}s")
        logger.log(f"That is {1. / _aver} frames per second")

    if profiling:
        logger.log("====================================================")
        logger.log("model profiling...")
        tensor = torch.rand(input_shape)
        if next(model.parameters()).is_cuda:
            tensor = tensor.cuda()
        tensor = (tensor,)
        flops, params = _profile(model, inputs=tensor)
        logger.log(f"Model FLOPs = {flops/1e9}, params = {params/1e6}")
