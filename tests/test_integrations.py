def test_package_installed():
    from neetbox.integrations import pkg

    package_name = "opencv-python"
    package_name_import = "cv2"
    installed = pkg.is_installed(
        package=package_name_import, try_install_if_not=False
    )
    print(f"is '{package_name}' installed? {installed}")


def test_device_info():
    from neetbox.integrations import env

    for cpu in env.cpus:
        print(cpu)


def test_resource_loader():
    from neetbox.integrations.resource import ResourceLoader
    import os

    file_type = "py"
    ldr = ResourceLoader("./", file_types=[file_type])
    print(f"found {len(ldr.get_file_list())} {file_type} files")
    assert len(ldr.get_file_list()) == len(
        [y for x in os.walk("./") for y in x[2] if y.endswith(".py")]
    )

def test_download():
    from neetbox.integrations.resource import download
    urls = {
        'readme.md':'https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/readme.md',
        'some.jpg':'https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/res/driving.jpg'
    }
    res = download(urls=urls,verbose=True)
    print(res)
    import os
    for fname,furl in urls:
        os.remove(fname)
    
test_resource_loader()
