def test_package_installed():
    from neetbox.utils import pkg
    installed = pkg.is_installed("torch", terminate=False)
    print(f"is 'torch' installed? {True}")


# def test_device_info():
#     from neetbox.utils import device
#     gpus = device.gpus()
#     for gpu in gpus:
#         # get the GPU id
#         gpu_id = gpu.id
#         # name of GPU
#         gpu_name = gpu.name
#         # get % percentage of GPU usage of that GPU
#         gpu_load = f"{gpu.load*100}%"
#         # get free memory in MB format
#         gpu_free_memory = f"{gpu.memoryFree}MB"
#         # get used memory
#         gpu_used_memory = f"{gpu.memoryUsed}MB"
#         # get total memory
#         gpu_total_memory = f"{gpu.memoryTotal}MB"
#         # get GPU temperature in Celsius
#         gpu_temperature = f"{gpu.temperature} °C"
#         gpu_uuid = gpu.uuid
#         gpus.append((
#             gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
#             gpu_total_memory, gpu_temperature, gpu_uuid
#         ))
#     for gpu in gpus:
#         print(gpu)