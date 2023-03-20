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
from neetbox.logging import logger
from neetbox.utils import package
from neetbox.integrations import engine


class ImageFolder:
    def __init__(self, folder, sub_dirs=True, async_scan=False):
        self.path = folder
        self.image_path_list = []
        self._initialized = False
        self._ready = False
        self._scan_sub_dirs = sub_dirs
        self._async_scan = async_scan
        self._scan()

    def _scan(self):
        if not self._ready and self._initialized:
            raise Exception("another scanning requested during the previous one.")
        self._ready = False

        def perform_scan():
            image_path_list = []
            dirs = [self.path]
            while len(dirs) != 0:
                dir_now = dirs.pop()
                for item in os.scandir(dir_now):
                    if item.is_dir() and self._scan_sub_dirs:
                        dirs.append(item.path)
                    elif item.is_file():
                        if item.name.endswith(".jpg") or item.name.endswith(".png"):
                            image_path_list.append(item.path)
            self.image_path_list = image_path_list
            self._ready = True
            if not self._initialized:
                self._initialized = True
            logger.log(f"Folder ready with {len(image_path_list)} images.")

        if self._async_scan:
            import threading

            threading.Thread(target=perform_scan).start()
        else:
            perform_scan()

    def get_image_list(self):
        if not self._ready:
            raise Exception("not ready.")
        return self.image_path_list.copy()

    def __getitem__(self, index):
        if not self._ready:
            raise Exception("not ready.")
        if type(index) is int:
            return self.image_path_list[index]

    def get_random_image(self):
        rand_img_path = self.image_path_list[int(random() * len(self.image_path_list))]
        image = Image.open(rand_img_path).convert("RGB")
        return image

    def get_random_images(self, howmany=1):
        assert howmany < len(self.image_path_list)
        rand_idx_begin = int(random() * (len(self.image_path_list) - howmany))
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
            assert package.is_installed("torchvision", terminate=True)
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
