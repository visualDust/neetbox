# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

from PIL import Image
from random import random
import os
import asyncio
import numpy as np
import threading
from neetbox.integrations import pkg
from neetbox.logging import logger
from neetbox.integrations import engine
from typing import Dict
import pathlib


_loader_pool: Dict[
    str, "ResourceLoader"
] = dict()  # all ResourceLoaders are stored here


class ResourceLoader:
    _ready: bool = False  # stands for each scan
    file_path_list: list = []
    _initialized: bool = False  # stands for the first scan on creation

    def __new__(
        cls,
        folder,
        file_types=["png", "jpg"],
        sub_dirs=True,
        async_scan=False,
        *args,
        **kwargs,
    ):
        _id = "full_scan_" if sub_dirs else "partial_scan_" + folder + str(file_types)
        if not _id in _loader_pool:
            _loader_pool[_id] = super(ResourceLoader, cls).__new__(cls, *args, **kwargs)
        return _loader_pool[_id]

    def __init__(
        self, folder, file_types=["png", "jpg"], sub_dirs=True, async_scan=False
    ):
        super().__init__()
        self.path = folder
        self._file_types = file_types
        self._scan_sub_dirs = sub_dirs
        self._async_scan = async_scan
        if not self._ready:
            self._scan()

    def _scan(self):
        if not self._ready and self._initialized:
            raise Exception("another scanning requested during the previous one.")
        self._ready = False

        def can_match(path: pathlib.Path):
            if not path.is_file():
                return False
            pattern = '**/*.' if self._scan_sub_dirs else '*.'
            for file_type in self._file_types:
                if path.match(pattern + file_type):
                    return True
            return False

        def perform_scan():
            self.file_path_list = [str(path) for path in pathlib.Path(
                self.path).glob('**/*') if can_match(path)]
            self._ready = True
            if not self._initialized:
                self._initialized = True
            logger.ok(f"Resource loader '{self.path}' ready with {len(self.file_path_list)} files.")

        if self._async_scan:
            threading.Thread(target=perform_scan).start()
        else:
            perform_scan()

    def get_file_list(self):
        if not self._ready:
            raise Exception("not ready.")
        return self.file_path_list.copy()

    def __getitem__(self, index):
        if not self._ready:
            raise Exception("not ready.")
        if type(index) is int:
            return self.file_path_list[index]

class ImagesLoader(ResourceLoader):
    
    def get_random_image(self):
        rand_img_path = self.file_path_list[int(random() * len(self.file_path_list))]
        image = Image.open(rand_img_path).convert("RGB")
        return image

    def get_random_images(self, howmany=1):
        assert howmany < len(self.file_path_list)
        rand_idx_begin = int(random() * (len(self.file_path_list) - howmany))
        image_path_list = self[rand_idx_begin : rand_idx_begin + howmany]
        image_list = []
        for path in image_path_list:
            image_list.append(Image.open(path).convert("RGB"))
        return image_list

    def get_random_image_as_numpy(self):
        image = self.get_random_image()
        return np.array(image)

    def get_random_image_as_tensor(self, engine=engine.Torch):
        assert engine in [engine.Torch]  # todo support other engines
        if engine == engine.Torch:
            assert pkg.is_installed("torchvision")
            import torchvision.transforms as T

            tensor_transform = T.Compose(
                [
                    T.ToTensor(),
                    T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
                ]
            )
            image = tensor_transform(self.get_random_image()).unsqueeze(
                0
            )  # To tensor of NCHW
            return image

    # todo to_dataset
