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