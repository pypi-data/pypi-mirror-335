import os
from operator import eq

import cv2
import numpy as np
import scipy.io
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from datetime import datetime
import tensorflow as tf
from keras import Sequential

# from tensorboardX import SummaryWriter
from utils import DataSet, validate, show_confMat  # 自定义类
from net import Net  # 导入模型
import torch
from net import Net
import matplotlib.pyplot as plt
from skimage import io, img_as_float
from skimage.metrics import structural_similarity as compare_ssim, structural_similarity


# def read_data(path):
#     for file in os.listdir(path):
#         temp=scipy.io.loadmat(os.path.join(path,file))
#         print(temp)
#
# read_data('D:\dataset\patch')

def get_A_single_input(idx):
    path = 'D:\dataset\patch'
    testing_dataset = DataSet(path=path, train=False)

    test_loader = torch.utils.data.DataLoader(
        dataset=testing_dataset,
        batch_size=100,
        shuffle=True
    )
    for batch_idx, data in enumerate(test_loader):
        inputs, labels = data
        # print(len(inputs))
        return inputs[idx], labels[idx]


def predict(model, idx):
    input, lable = get_A_single_input(idx)
    input = input.reshape(1, 103, 17, 17)
    output = model(input)
    output = output.detach().numpy()
    return output


# 计算扰动距离L2范数
def calculate_l2(org_image, adv_image):
    org_image = org_image[:, :, :-1]
    adv_image = adv_image[:, :, :-1]
    # 转换图像为 numpy 数组
    img1_arr = np.array(org_image)
    img2_arr = np.array(adv_image)

    # 如果图像是彩色的，需要将其展平为一维向量
    img1_arr = img1_arr.flatten()
    img2_arr = img2_arr.flatten()

    # 计算两张图像之间的 L2 范数
    l2 = np.sqrt(np.sum((img1_arr - img2_arr) ** 2))

    print('L2 norm between the two images:', l2)


# 计算扰动距离L2范数
def l2_norm(img1, img2):
    # 获取图片的高度和宽度
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    # 将两张图片转换为NumPy数组格式
    img1_array = np.array(img1)
    img2_array = np.array(img2)

    # 定义一个空的矩阵用于存储结果
    result = np.zeros((h1 + h2, w1 + w2))

    # 将两张图片按顺序拼接在一起
    for i in range(0, h1):
        for j in range(0, w1):
            result[i + h2, j + w2] = cv2.matchTemplate(img1_array[i:i + h2, j:j + w2], img2_array[i:i + h2, j:j + w2],
                                                       cv2.TM_CCOEFF_NORMED)

    # 计算L2范数并输出结果
    l2norm = np.linalg.norm(result, ord=2)
    print("L2 norm:", l2norm)


def calculate_ssim(org_image, adv_image2):
    # 读取两幅图像
    img1 = img_as_float(org_image)
    img2 = img_as_float(adv_image2)

    # 计算 SSIM
    ssim = structural_similarity(img1, img2, channel_axis=2)
    ssim_normalized = (ssim + 1) / 2

    print('Structural Similarity Index between the two images:', ssim, ssim_normalized)
    return ssim_normalized


# 读取第一张图片
image1 = cv2.imread("../data/MSTAR/T62/HB14931.JPG")
# 读取第二张图片
image2 = cv2.imread("../adversarial_attack/T62/HB14931.JPG")

# calculate_l2(image1, image1)
# calculate_l2(image1, image2)
# calculate_ssim(image1, image2)

val = [0, 0, 0]
result = eq(val.all(), [255, 255, 255])
print(result)

# model = Sequential()
# model = tf.keras.models.load_model(r'model.h5')

# model = Net()
# model.load_state_dict(torch.load('vgg.pth'))
# # model = torch.load('/root/tf-logs/11-30_21-26-28/net_params.pkl')
# model.eval()
# model=model.double()
#
#
# output=predict(model,0)
# label=np.argmax(output)
# print(output)
# print(label)
# input,label=get_A_single_input()
# # print(input.shape)
# # input=input.reshape(1,103,17,17)
# output=model(input)
# for o in output.data:
#     print(o)
#     print(o[8])
# # print(ll)
# _, predicted = torch.max(output.data, 1)
# print(predicted)
# image = cv2.imread("HB19487.JPG")
# image2 = cv2.imread("TEST_IMAGE.JPEG")
# image = cv2.resize(image, (368, 368))
# image2 = cv2.resize(image2, (368, 368))
# image1_np = np.array(image, dtype=np.float32)
# image2_np = np.array(image2, dtype=np.float32)
# print(image.shape)
# print(image2.shape)
# if image2.size == image.size:
#     image_diff = np.abs(image1_np - image2_np)
#     infinity_norm = np.max(image_diff)
#     print(infinity_norm)
# else:
#     print("图片大小不一样")
# predshape = (1, 368, 368, 3)
# im_pred = image.reshape(predshape)
# im_pred = im_pred.astype('float')
#
# prob = model.predict(im_pred)
# print(prob)
# print(prob.shape)
# print(prob[0][6])
