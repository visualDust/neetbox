from PIL import Image
from random import random
import os
import numpy as np

class ImageFolder:
    def __init__(this, folder, sub_dirs=False, async_scan = False):
        this.folder_path = folder
        this.image_path_list = []
        this.tensor_transform = None
        this._initialized = False
        this._ready = False
        this._scan_sub_dirs = sub_dirs
        this._async_scan = async_scan
        this._scan()

    def _scan(this):
        if not this._ready and this._initialized:
            raise Exception("another scanning requested during the previous one.")
        this._ready = False
        def perform_scan():
            image_path_list = []
            dirs = [this.folder_path]
            while len(dirs) != 0:
                dir_now = dirs.pop()
                for item in os.scandir(dir_now):
                    if item.is_dir() and this._scan_sub_dirs:
                        dirs.append(item.path)
                    elif item.is_file():
                        if item.name.endswith('.jpg') or item.name.endswith('.png'):
                            image_path_list.append(item.path)
            this.image_path_list =image_path_list
            this._ready = True
            if not this._initialized:
                this._initialized = True
            print('Folder Ready.')
        if this._async_scan:
            import threading
            threading.Thread(target=perform_scan).start()
        else:
            perform_scan()

    def get_image_list(this):
        if not this._ready:
            raise Exception("not ready.")
        return this.image_path_list.copy()

    def __getitem__(this, index):
        if not this._ready:
            raise Exception("not ready.")
        if type(index) is int:
            return this.image_path_list[index]    
    
    def get_random_image(this):
        rand_img_path = this.image_path_list[int(random() * len(this.image_path_list))]
        image = Image.open(rand_img_path).convert("RGB")
        return image
    
    def get_random_images(this, howmany = 1):
        assert howmany < len(this.image_path_list)
        rand_idx_begin = int(random() * (len(this.image_path_list)-howmany))
        image_path_list = this[rand_idx_begin:rand_idx_begin+howmany]
        image_list = []
        for path in image_path_list:
            image_list.append(Image.open(path).convert("RGB"))
        return image_list

    def get_random_image_as_numpy(this):
        image = this.get_random_image()
        return np.array(image)

    def get_random_image_as_tensor(this):
        if this.tensor_transform is None:
            import torchvision.transforms as T
            this.tensor_transform = T.Compose([
                    T.ToTensor(),
                    T.Normalize(mean = (0.5, 0.5, 0.5), std = (0.5, 0.5, 0.5)),
                ])
        image = this.tensor_transform(this.get_random_image()).unsqueeze(0)# To tensor of NCHW
        return image