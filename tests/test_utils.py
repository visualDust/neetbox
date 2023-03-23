def test_package_installed():
    from neetbox.utils import pkg
    installed = pkg.is_installed("torch", terminate=False)
    print(f"is 'torch' installed? {True}")


def test_device_info():
    from neetbox.utils import env
    for cpu in env.cpus:
        print(cpu)

def test_resource_loader():
    from neetbox.utils.resource import ResourceLoader
    file_type = 'py'
    ldr = ResourceLoader('./',file_types=[file_type])
    print(f'found {len(ldr.get_file_list())} {file_type} files')
    