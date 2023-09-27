# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

from random import random
import os
from neetbox.utils import pkg

import numpy as np
import threading
from neetbox.logging import logger
from neetbox.integrations import engine
from typing import Iterable
from typing import Dict
import pathlib
import signal
from functools import partial
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import List, Union, Dict, Any
from rich.progress import track
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from PIL import Image

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
                if path.match("*." + file_type):
                    return True
            return False

        def perform_scan():
            glob_str = "**/*" if self._scan_sub_dirs else "*"
            if not verbose:  # do not output
                self.file_path_list = [
                    str(path)
                    for path in pathlib.Path(self.path).glob(glob_str)
                    if can_match(path)
                ]
            else:
                self.file_path_list = []
                for path in pathlib.Path(self.path).glob(glob_str):
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
    def __init__(
        self,
        folder,
        file_types=["png", "jpg"],
        sub_dirs=True,
        async_scan=False,
        verbose=False,
    ):
        pkg.is_installed("PIL", try_install_if_not="pillow")

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
    max_workers=4,
):
    """download both online and local files from urls

    Example: download('')

    Args:
        urls (Union[str, List[str], Dict[str, str]]): single str to download from url; list of strs to download from urls; dict(filename:url) to download urls and rename them to filenames
        filenames (Union[str, List[str]], optional): str to rename the downloaded file; list of strs to rename downloaded files; None means no rename. Defaults to None.
        overwrite Bool: whether to skip exist files. Default to True.
        retry (int, optional): retries when error occures. Defaults to 3.
        verbose (bool, optional): tell what happening in output. Defaults to True.
    """
    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    done_event = Event()

    def handle_sigint(signum, frame):
        done_event.set()

    signal.signal(signal.SIGINT, handle_sigint)

    def copy_url(task_id: TaskID, url: str, path: str) -> None:
        """Copy data from a url to a local file."""
        response = urlopen(url)
        # This will break if the response doesn't contain content length
        progress.update(task_id, total=int(response.info()["Content-length"]))
        with open(path, "wb") as dest_file:
            progress.start_task(task_id)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task_id, advance=len(data))
                if done_event.is_set():
                    return
        logger.log(f"Downloaded {path}.")

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

    with progress:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for fname, url in urls.items():
                filename = url.split("/")[-1]
                dest_path = os.path.join(fname)
                task_id = progress.add_task("download", filename=filename, start=False)
                pool.submit(copy_url, task_id, url, dest_path)
