import pandas as pd
import torch
from skimage import img_as_float
from skimage.metrics import structural_similarity
from torch import nn

import torch.nn.functional as F
from torch.nn import Sequential
import tensorflow as tf
from torchvision import models
from torchvision import transforms

from DFMCS import DFMCS_Parameters
from DFMCS import DFMCS
from MCTS_DUT import MCTS_Parameters
from MCTS_DUT import MCTS
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from net import Net
import time

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# print(tensorflow.reduce_sum(tensorflow.random.normal([1000, 1000])))

# VGG16模型训练
# model = keras.applications.vgg16.VGG16()
# print(model)
# model = Sequential()
model = torch.load("ResNet50_for_MSTAR_6_4_91.0.pth", map_location=torch.device('cpu'))
# model.eval()
# model = torch.load('VGG16_for_RESISC45.pth')
ImageName = []
QUERY_NUM = []
ATTACK_NUM = []
SSIM = []
SUCCESS_RATE = []
RAW_CLASS = []
ADV_CLASS = []
Time = []


# model = keras.applications.resnet50.ResNet50(weights='imagenet')


# 加载模型
# model = Net()
# model.load_state_dict(torch.load('vgg.pth'))
# # model = torch.load('/root/tf-logs/11-30_21-26-28/net_params.pkl')
# model.eval()
# model=model.double()
# 获取数据集的图片
# input = get_A_single_input(0)
# input = input[0].reshape(1, 103, 17, 17)
# # print(input)
# image = input[0].numpy()
# imagenet_class = "2"
# image = cv2.imread("TEST_IMAGE.JPEG")
# image = cv2.imread("HB19487.JPG")
# image = image.reshape(1, 368, 368, 3)
# im_pred = image.astype('float')

# 计算扰动距离L2范数
def calculate_ssim(org_image, adv_image2):
    # 读取两幅图像
    img1 = img_as_float(org_image)
    img2 = img_as_float(adv_image2)

    # 计算 SSIM
    ssim = structural_similarity(img1, img2, channel_axis=2)
    ssim_normalized = (ssim + 1) / 2

    # print('Structural Similarity Index between the two images:', ssim, ssim_normalized)
    return ssim_normalized


def pre_image(img):
    trans_val = transforms.Compose(
        [transforms.ToTensor(),
         transforms.Resize((224, 224))
         ])
    im_pred = trans_val(img).unsqueeze(0)
    return im_pred


# def handle_image(file_pathname):
#     failure_num = 0
#     num_png = 0
#     # 遍历该目录下的所有图片文件
#     for filename in os.listdir(file_pathname):
#         print(file_pathname + '/' + filename)
#         if os.path.isfile(file_pathname + '/' + filename):
#             print(file_pathname + '/' + filename)
#             # 把攻击的图片名称保存
#             ImageName.append(filename)
#             # img = cv2.imread(file_pathname + '/' + filename + '.jpg')
#             img = cv2.imread(file_pathname + '/' + filename)
#             # img_pre = np.float32(img)
#             # plt.imshow(img)
#             # plt.show()
#             start_time = time.time()
#             image = img[:, :, ::-1]
#             img_pre = cv2.resize(image, (368, 368))
#             pred_shape = (1, 368, 368, 3)
#             im_pred = pre_image(img)
#             prob = model.predict(im_pred)
#             pred = np.argmax(np.asarray(prob))
#             print("当前分类：%s" % pred)
#             RAW_CLASS.append(pred)
#             params_for_run = MCTS_Parameters(img_pre, int(pred), model, pred_shape)
#             params_for_run.verbose = True
#             params_for_run.simulations_cutoff = 2
#             params_for_run.backtracking_constant = 50
#             best_image, sev, new_pred, statistics, query, attack_result = dut-sar(params_for_run)
#             print("完成对一张图片的攻击！", attack_result)
#             # new_pred = np.argmax(np.asarray(new_prob))
#             print(pred, new_pred)
#             end_time = time.time()
#             execution_time = end_time - start_time
#             Time.append(execution_time)
#             num_png = num_png + 1
#             if pred == new_pred:
#                 failure_num += 1
#                 print("攻击失败！")
#                 QUERY_NUM.append(-1)
#                 ATTACK_NUM.append(-1)
#                 SSIM.append(-1)
#                 ADV_CLASS.append(-1)
#                 SUCCESS_RATE.append(-1)
#                 continue
#             sum_query = query + 1
#             ssim = calculate_ssim(img_pre, best_image)
#             QUERY_NUM.append(sum_query)
#             ATTACK_NUM.append(sev)
#             SSIM.append(ssim)
#             n_prob = model.predict(best_image.reshape(1, 368, 368, 3))
#             new_class = np.argmax(prob)
#             new_prob = n_prob[0][new_class]
#             ADV_CLASS.append(new_pred)
#             # save figure
#             cv2.imwrite('../adversarial_attack/T62/' + filename, best_image)
#             # cv2.imwrite('D:/dut-sar/dut-sar-SAR/test/analysis/adversarial_attack' + filename, best_image)
#
#             print("对抗样本保存成功！")
#             # files = os.listdir(file_pathname)  # 读入文件夹
#             # num_png = len(files)  # 统计文件夹中的文件个数
#             succ_rate = (num_png - failure_num) / num_png
#             SUCCESS_RATE.append(succ_rate)
#             analysis = [ImageName, ATTACK_NUM, QUERY_NUM, SSIM, SUCCESS_RATE, RAW_CLASS, ADV_CLASS, Time]
#             print("攻击次数：%s, 扰动距离：%s, 原始分类：%s, 新的分类: %s, 攻击所用时间：%s 秒" %(analysis[1], analysis[3], analysis[5], analysis[6], analysis[7]))
#             name = ['ImageName', 'Number of attacks', 'Number of Queries', 'SSIM', 'SUCCESS RATE', 'Raw Class',
#                     'Adv Class', 'Time']
#             # print(analysis)
#             # print(len(analysis))
#             # print("攻击成功率为：", succ_rate)
#             # df = pandas.DataFrame(analysis, columns=name) # 数据有三列，列名分别为one,two,three
#             # df = pd.DataFrame.from_dict(dict(zip(name, analysis)), orient='index')
#             df = pd.DataFrame(dict(zip(name, analysis)))
#
#             # 数据导出为csv
#             df.to_excel('../data/analysis/T62/result_analysis_compare.xls')
#             # df.to_excel('../test/analysis/result_analysis.xls')
#
#             # plt.clf()
#             # a, = plt.plot(statistics[0], label="Min Severity Found")
#             # b, = plt.plot(statistics[1], label="Severity per Iteration")
#             # c, = plt.plot(statistics[2], label="Rolling Average Severity")
#             # plt.legend(handles=[a, b, c], loc='center left', bbox_to_anchor=(1, 0.5))
#             # plt.title("Single Run dut-sar Statisitcs")
#             # plt.xlabel("Iteration")
#             # plt.ylabel("L_0 Severity")
#             # plt.savefig('D:/dut-sar/dut-sar-SAR/runs_analysis/2S1/' + filename, dpi=300)
#         else:
#             print("The file" + file_pathname + '/' + filename + " does not exist.")
#             continue


def handle_image(file_pathname):
    failure_num = 0
    num_png = 0
    # 遍历该目录下的所有图片文件
    for filename in os.listdir(file_pathname):
        files = os.listdir(file_pathname + '/' + filename)
        for f in files:
            if os.path.isfile(file_pathname + '/' + filename + '/' + f):
                print(file_pathname + '/' + filename + '/' + f)
                # img = cv2.imread(file_pathname + '/' + filename + '.jpg')
                # 把攻击的图片名称保存
                ImageName.append(filename + '/' + f)
                # img = cv2.imread(file_pathname + '/' + filename + '.jpg')
                img = cv2.imread(file_pathname + '/' + filename + '/' + f)
                image = img[:, :, ::-1]
                # img_pre = np.float32(img)
                # plt.imshow(img)
                # plt.show()
                start_time = time.time()
                im_pred = pre_image(img)
                prob = model(im_pred)
                prob = F.softmax(prob, dim=1).detach().numpy()
                pred = np.argmax(np.asarray(prob))
                print("当前分类：%s" % pred)
                RAW_CLASS.append(pred)
                params_for_run = MCTS_Parameters(img, int(pred), model, (1, 3, 224, 224))
                params_for_run.verbose = True
                params_for_run.simulations_cutoff = 3
                params_for_run.backtracking_constant = 50
                best_image, sev, new_pred, statistics, query, attack_result = MCTS(params_for_run)
                print("完成对一张图片的攻击！", attack_result)
                # new_pred = np.argmax(np.asarray(new_prob))
                print(pred, new_pred)
                end_time = time.time()
                execution_time = end_time - start_time
                Time.append(execution_time)
                num_png = num_png + 1
                if pred == new_pred:
                    failure_num += 1
                    print("攻击失败！")
                    QUERY_NUM.append(-1)
                    ATTACK_NUM.append(-2)
                    SSIM.append(-1)
                    ADV_CLASS.append(-1)
                    SUCCESS_RATE.append(-1)
                    continue
                sum_query = query + 1
                ssim = calculate_ssim(image, best_image)
                QUERY_NUM.append(sum_query)
                ATTACK_NUM.append(sev)
                SSIM.append(ssim)
                n_prob = model(pre_image(best_image)).detach().numpy()
                new_class = np.argmax(prob)
                new_prob = n_prob[0][new_class]
                ADV_CLASS.append(new_pred)
                # save figure
                cv2.imwrite('../adversarial_attack/' + filename + '/' + f, best_image)
                # cv2.imwrite('D:/dut-sar/dut-sar-SAR/test/analysis/adversarial_attack' + filename, best_image)

                print("对抗样本保存成功！")
                # files = os.listdir(file_pathname)  # 读入文件夹
                # num_png = len(files)  # 统计文件夹中的文件个数
                succ_rate = (num_png - failure_num) / num_png
                SUCCESS_RATE.append(succ_rate)
                analysis = [ImageName, ATTACK_NUM, QUERY_NUM, SSIM, SUCCESS_RATE, RAW_CLASS, ADV_CLASS, Time]
                print("攻击次数：%s, 扰动距离：%s, 原始分类：%s, 新的分类: %s, 攻击所用时间：%s 秒" % (
                    analysis[1], analysis[3], analysis[5], analysis[6], analysis[7]))
                name = ['ImageName', 'Number of attacks', 'Number of Queries', 'SSIM', 'SUCCESS RATE', 'Raw Class',
                        'Adv Class', 'Time']
                # print(analysis)
                # print(len(analysis))
                # print("攻击成功率为：", succ_rate)
                # df = pandas.DataFrame(analysis, columns=name) # 数据有三列，列名分别为one,two,three
                # df = pd.DataFrame.from_dict(dict(zip(name, analysis)), orient='index')
                df = pd.DataFrame(dict(zip(name, analysis)))

                # 数据导出为csv
                df.to_excel('../data/analysis/result_analysis_1000s.xls')
                # df.to_excel('../test/analysis/result_analysis.xls')/
            else:
                print("The file" + file_pathname + '/' + filename + " does not exist.")
                continue


if __name__ == "__main__":
    # handle_image('../test_ima')
    handle_image('../data/test')
