import torch
import tensorflow as tf
import cv2
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


print("Torch:")
print(torch.cuda.is_available())
print(torch.cuda.current_device())
print(torch.cuda.get_device_name(0))

print("CV2:")
if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    print('Yes')
    print(cv2.cuda.printCudaDeviceInfo(0))
else:
    print('No')


print("Tensorflow:")
print(tf.__version__)
print(tf.config.list_physical_devices())
print(tf.test.is_gpu_available())
print(tf.test.is_built_with_cuda())
print(tf.sysconfig.get_build_info()['cuda_version'])

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

