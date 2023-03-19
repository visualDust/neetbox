def test_package_installed():
    from neetbox.utils import package
    installed = package.is_installed("torch")
    print(f"is 'torch' installed? {True}")
