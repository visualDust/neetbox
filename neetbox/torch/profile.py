# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

from thop import profile as _profile
from neetbox.core import *
import time
from tqdm import tqdm
import torch

logger = get_static_logger()


def profile(model, input_shape=(1, 3, 2048, 1024), specific_input = None, profiling=True, speedtest=1000):
    if speedtest:
        input_tensor = specific_input
        if not input_tensor:
            input_tensor = torch.rand(input_shape)
            if next(model.parameters()).is_cuda:
                input_tensor = input_tensor.cuda()
        counter = []
        logger.log("running speedtest...")
        model.eval()
        with torch.no_grad():
            logger.log("start warm up")
            for i in tqdm(range(10)):
                model(input_tensor)
            logger.log("warm up done")
            for test_index in tqdm(range(speedtest + 2)):
                t = time.time()
                output = model(input_tensor)
                counter.append(time.time() - t)
            _min, _max, _sum = min(counter), max(counter), sum(counter)
        _aver = (_sum - _min - _max) / speedtest
        fps_str = f"average {_aver}s per run"
        if type(output) in [list,torch.Tensor]:
            if type(output) is list:
                output_shape = f"{len(output)}-element-list\n"
            else:
                output_shape = output.shape
            fps_str += f" with out put size {output_shape}"
        logger.log(fps_str)
        logger.log(f"min inference time: {_min}s, Max inference time: {_max}s")
        _fps_aver = 1. / _aver
        logger.log(f"That is {_fps_aver} frames per second")

        if next(model.parameters()).is_cuda:
            logger.log("====================================================")
            time_counter = torch.zeros((speedtest + 2, 1))
            time0, time1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(
                enable_timing=True
            )
            model.eval()
            with torch.no_grad():
                logger.log("running CUDA side synchronous speedtest...")
                for test_index in tqdm(range(speedtest + 2)):
                    time0.record()
                    output = model(input_tensor)
                    time1.record()
                    torch.cuda.synchronize()
                    time_counter[test_index] = time0.elapsed_time(time1)
                _min, _max, _sum = (
                    time_counter.min(),
                    time_counter.max(),
                    time_counter.sum(),
                )
                _aver = (_sum - _min - _max)/ 1000. / speedtest
                fps_str = f"average {_aver}s per run"
                if type(output) in [list,torch.Tensor]:
                    if type(output) is list:
                        output_shape = f"{len(output)}-element-list\n"
                    else:
                        output_shape = output.shape
                    fps_str += f" with out put size {output_shape}"
                logger.log(fps_str)
                logger.log(
                    f"min inference time: {_min / 1000.}s, max inference time: {_max / 1000.}s"
                )
                logger.log(f"That is {1. / _aver} frames per second")
                if _fps_aver - 1. / _aver > 10.:
                    logger.warn(f"Seems your model has an imbalanced performance peek between CUDA side synchronous test and none-sync one. Consider raising speedtest loop times (currently {speedtest} +2) to have a stable result.")
                logger.debug(f"Note that the CUDA side synchronous speedtest is more reliable since you are using a GPU.")
    if profiling:
        if speedtest:
            logger.log("====================================================")
        logger.log("model profiling...")
        input_tensor = specific_input
        if not input_tensor:
            input_tensor = torch.rand(input_shape)
            if next(model.parameters()).is_cuda:
                input_tensor = input_tensor.cuda()
        input_tensor = (input_tensor,)
        flops, params = _profile(model, inputs=input_tensor)
        logger.log(f"Model FLOPs = {flops/1e9}G, params = {params/1e6}M")
