def test_package_installed():
    from neetbox.utils import pkg
    installed = pkg.is_installed("torch", terminate=False)
    print(f"is 'torch' installed? {True}")


def test_device_info():
    from neetbox.utils import env
    for cpu in env.cpus:
        print(cpu)