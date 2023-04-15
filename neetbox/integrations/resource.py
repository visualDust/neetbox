# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

from random import random
import os
import asyncio
import numpy as np
import threading
from neetbox.utils import pkg
from neetbox.logging import logger
from neetbox.integrations import engine
from typing import Dict
import pathlib
import urllib.request
from tqdm import tqdm
from typing import List, Union, Dict, Any


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
        _id = folder + str(file_types) + "_R" if sub_dirs else ""
        if _id in _loader_pool:
            logger.info(
                "ResourceLoader with same path and same file types already exists. Returning the old one."
            )
        else:
            _loader_pool[_id] = super(ResourceLoader, cls).__new__(cls)
        return _loader_pool[_id]

    def __init__(
        self,
        folder,
        file_types=["png", "jpg"],
        sub_dirs=True,
        async_scan=False,
        verbose=False,
    ):
        super().__init__()
        self.path = folder
        self._file_types = file_types
        self._scan_sub_dirs = sub_dirs
        self._async_scan = async_scan
        if not self._ready:
            self._scan(verbose)

    def _scan(self, verbose):
        if not self._ready and self._initialized:
            raise Exception("another scanning requested during the previous one.")
        self._ready = False

        def can_match(path: pathlib.Path):
            if not path.is_file():
                return False
            for file_type in self._file_types:
                if path.match('*.' + file_type):
                    return True
            return False

        def perform_scan():
            glob_str = '**/*' if self._scan_sub_dirs else "*"
            if not verbose:  # do not output
                self.file_path_list = [
                    str(path)
                    for path in pathlib.Path(self.path).glob(glob_str)
                    if can_match(path)
                ]
            else:
                self.file_path_list = []
                for path in tqdm(pathlib.Path(self.path).glob(glob_str)):
                    if can_match(path):
                        self.file_path_list.append(path)
            self._ready = True
            if not self._initialized:
                self._initialized = True
            logger.ok(
                f"Resource loader '{self.path}' ready with {len(self._file_types)} file types({len(self.file_path_list)} files)."
            )

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
    
    def __init__(self, folder, file_types=["png", "jpg"], sub_dirs=True, async_scan=False, verbose=False):
        pkg.is_installed('PIL', try_install_if_not='pillow')
        from PIL import Image
        super().__init__(folder, file_types, sub_dirs, async_scan, verbose)
        
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


def download(
    urls: Union[str, List[str], Dict[str, str]],
    filenames: Union[str, List[str]] = None,
    overwrite=True,
    retry=3,
    verbose=True,
):
    """download both online and local files from urls

    Example: download('')

    Args:
        urls (Union[str, List[str], Dict[str, str]]): single str to download from url; list of strs to download from urls; dict(filename:url) to download urls and rename them to filenames
        filenames (Union[str, List[str]], optional): str to rename the downloaded file; list of strs to rename downloaded files; None means no rename. Defaults to None.
        overwrite Bool: whether to skip exist files. Default to True.
        retry (int, optional): retries when error occures. Defaults to 3.
        verbose (bool, optional): tell what happening in output. Defaults to True.

    Returns:
        _type_: _description_
    """
    assert type(urls) in [str, list, dict], "unkown format of url"
    if type(urls) is str:
        assert (
            filenames is None
            or type(filenames) is str
            or (type(filenames) is list and len(filenames) == 1)
        ), "num of urls and filenames mismatch"
        urls = [
            urls,
        ]
        filenames = (
            [
                filenames,
            ]
            if filenames
            else None
        )
    if type(urls) is list:
        if filenames is None:
            filenames = [None] * len(urls)
        assert type(filenames) is list and len(urls) == len(
            filenames
        ), "num of urls and filenames mismatch"

        urls = {filenames[i]: urls[i] for i in range(len(urls))}

    logger.log(f"Downloading {len(urls)} file(s)...")

    if verbose:
        outer_pbar = tqdm(total=len(urls), desc=f"Overall process")

    _reporthook = None
    _results = []
    for fname, furl in tqdm(urls.items()):
        if fname and os.path.isfile(fname):
            if not overwrite:
                _results.append((fname,None))
                logger.log(
                    f"File {fname} already exists. If you want to redownload it, try to pass 'overwrite=True'"
                )
                continue
        if verbose:
            inner_pbar = tqdm(total=100, leave=False, desc=f"Currently downloading")

            def reporthook(p1, p2, p3):
                inner_pbar.total = p3
                inner_pbar.n = p1 * p2
                inner_pbar.refresh()

            _reporthook = reporthook
            outer_pbar.update(1)
        retry = 1 if not retry else retry
        while retry:
            try:
                res = urllib.request.urlretrieve(
                    url=furl, filename=fname, reporthook=_reporthook
                )
                _results.append(res)
                break
            except:
                retry -= 1
                logger.err(f"Download interrupt. {retry} retry(s) remaining.")
                if not retry:
                    raise RuntimeError(f"Download failed after retries")
    results = [fname for fname, reqmsg in _results]
    if not len(results):
        results = None
    if len(results) == 1:
        results = results[0]
    return results