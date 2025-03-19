import pytest

pytest.skip(allow_module_level=True)


def test_device_info():
    from neetbox.extension.machine import hardware

    for cpu in hardware.hardware["cpus"]:
        print(cpu)


def test_download():
    from neetbox.utils import download

    urls = {
        "somereadme.md": "https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/readme.md",
        "someimage.jpg": "https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/res/driving.jpg",
    }
    res = download(urls=urls, verbose=False)
    res = download(urls=urls, verbose=False, overwrite=False)
    print(res)
    import os

    for fname, furl in urls.items():
        os.remove(fname)
