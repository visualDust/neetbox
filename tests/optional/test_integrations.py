import pytest

pytest.skip(allow_module_level=True)


def test_device_info():
    from neetbox.extension.machine import hardware

    for cpu in hardware.hardware["cpus"]:
        print(cpu)


def test_resource_loader():
    import os

    from neetbox.utils import ResourceLoader

    file_type = "py"
    ldr = ResourceLoader("./", file_types=[file_type])
    print(f"found {len(ldr.get_file_list())} {file_type} files")
    file_os_walk = [y for x in os.walk("./") for y in x[2] if y.endswith(".py")]
    assert len(ldr.get_file_list()) == len(
        file_os_walk
    ), f"list length {len(ldr.get_file_list())} does not match {len(file_os_walk)}"

    file_type = "md"
    ldr = ResourceLoader("./", file_types=[file_type])
    from neetbox.utils import _loader_pool

    print(_loader_pool.keys())


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
