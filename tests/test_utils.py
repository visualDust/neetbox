from neetbox.utils import format


def test_package_installed():
    from neetbox.utils import pkg

    package_name = "opencv-python"
    package_name_import = "cv2"
    installed = pkg.is_installed(package=package_name_import, try_install_if_not=False)
    print(f"is '{package_name}' installed? {installed}")
