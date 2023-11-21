def test_download():
    from neetbox.integrations.resource import download

    print("testing download")
    urls = {
        "somereadme.md": "https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/readme.md",
        "someimage.jpg": "https://raw.githubusercontent.com/akasaki-is-a-rubbish/drivingaux/master/res/driving.jpg",
    }
    download(urls=urls)
    import os

    for fname, furl in urls.items():
        os.remove(fname)

def test_resource_loader():
    from neetbox.integrations.resource import ResourceLoader
    import time
    print("testing resource loader")
    md_loader = ResourceLoader('./',['md'])
    py_loader_async = ResourceLoader('./', async_scan=True,verbose=True)
    while not py_loader_async.ready:
        print("waiting resource loader")
        time.sleep(1)
    py_loader_async.get_file_list()
