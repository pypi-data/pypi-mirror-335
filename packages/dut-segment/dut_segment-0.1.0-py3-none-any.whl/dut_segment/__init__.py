import cv2
import pandas as pd
import torchvision
from skimage import img_as_float
from skimage.metrics import structural_similarity

from MCTS import MCTS_Parameters
from MCTS import MCTS
from PascalVOC import *

import os

import matplotlib.pyplot as plt
from torchvision import models

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# print(tensorflow.reduce_sum(tensorflow.random.normal([1000, 1000])))

# VGG16模型训练
# model = keras.applications.vgg16.VGG16()
# print(model)
# 图像分类SAR图像
# model = Sequential()
# model = tf.keras.models.load_model(r'model.h5')
# model = keras.applications.resnet50.ResNet50(weights='imagenet')
import torch

import torch
from net import Net

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

ImageName = []
QUERY_NUM = []
ATTACK_NUM = []
SSIM = []
SUCCESS_RATE = []
Raw_Classes = []
New_Classes = []
MIou = []


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


def handle_image(file_pathname, model, save_path):
    failure_num = 0
    num_png = 0
    # 遍历该目录下的所有图片文件
    for filename in os.listdir(file_pathname):
        if os.path.isfile(file_pathname + '/' + filename):
            print(file_pathname + '/' + filename)
            # img = cv2.imread(file_pathname + '/' + filename + '.jpg')
            org_image = cv2.imread(file_pathname + '/' + filename)
            new_image = org_image[:, :, ::-1]
            image_h, image_w, _ = new_image.shape
            predshape = (1, image_h, image_w, 3)
            # draw_image, pred, prob = predict(yolov3, image, True, image_path)
            # 原始分割图
            pre_output = seg_output(model, new_image)
            pred_label, raw_prob, draw_image = seg_predict(model, new_image)
            # 如果该图片中只识别到了背景，则不使用该图片
            if len(pred_label) == 1:
                for label in pred_label:
                    if label == 0:
                        print("该图片中没有类别！")
                        continue
            num_png = num_png + 1
            ImageName.append(filename)
            length = len(pred_label)
            Raw_Classes.append(pred_label)
            cv2.imwrite(save_path + '/raw/' + filename, draw_image)
            print("有几个分类：", length)
            # print(pred[0], prob[0])

            params_for_run = MCTS_Parameters(new_image, pred_label, model, length, predshape)
            params_for_run.verbose = False
            params_for_run.simulations_cutoff = 2
            params_for_run.backtracking_constant = 50
            best_image, sev, new_pred, statistics, query, attack_success = MCTS(params_for_run)
            # 保存对抗样本分割图
            pre_new_output = seg_output(model, best_image)
            # plt.imshow(best_image)
            # plt.show()
            if pred_label == new_pred:
                failure_num += 1
                print("攻击失败！")
                QUERY_NUM.append(-1)
                ATTACK_NUM.append(-1)
                SSIM.append(-1)
                SUCCESS_RATE.append(-1)
                # TP: 分类正确的样本个数; FP: 分类错误的样本个数; FN: 总共的样本个数
                # 查准率：TP/TP+FP; 查全率: TP/TP+FN
                New_Classes.append(pred_label)
                MIou.append(-1)
                continue
            iou = compute_seg_iou(pre_output, pre_new_output)
            print('平均交并比：', iou)
            MIou.append(iou)
            New_Classes.append(new_pred)
            print("攻击成功！", attack_success, failure_num)
            sum_query = query + 1
            ssim = calculate_ssim(new_image, best_image)
            QUERY_NUM.append(sum_query)
            ATTACK_NUM.append(sev)
            SSIM.append(ssim)
            new_pred, new_prob, best_draw = seg_predict(model, best_image)
            # save figure
            cv2.imwrite(save_path + '/draw/'
                        + filename, best_draw[:, :, ::-1])
            cv2.imwrite(save_path + '/adv_image/'
                        + filename, best_image[:, :, ::-1])

            # plt.clf()
            # a, = plt.plot(statistics[0], label="Min Severity Found")
            # b, = plt.plot(statistics[1], label="Severity per Iteration")
            # c, = plt.plot(statistics[2], label="Rolling Average Severity")
            # plt.legend(handles=[a, b, c], loc='center left', bbox_to_anchor=(1, 0.5))
            # plt.title("Single Run MCTS Statisitcs")
            # plt.xlabel("Iteration")
            # plt.ylabel("L_0 Severity")
            # plt.savefig('D:/practise/SafeCV-segment/SafeCV/analysis/test/runs_analysis/' + filename, dpi=300)
        else:
            print("The file" + file_pathname + '/' + filename + " does not exist.")

        # files = os.listdir(file_pathname)  # 读入文件夹
        # num_png = len(files)  # 统计文件夹中的文件个数
        succ_rate = (num_png - failure_num) / num_png
        SUCCESS_RATE.append(succ_rate)
        analysis = [ImageName, ATTACK_NUM, QUERY_NUM, SSIM, SUCCESS_RATE, Raw_Classes, New_Classes, MIou]
        print(analysis)
        name = ['ImageName', 'Number of attacks', 'Number of Queries', 'SSIM', 'SUCCESS RATE',
                'RAW Classes', 'New Classes', 'MIou']
        # print(analysis)
        # print(len(analysis))
        # print("攻击成功率为：", succ_rate)
        # df = pandas.DataFrame(analysis, columns=name) # 数据有三列，列名分别为one,two,three
        df = pd.DataFrame(dict(zip(name, analysis)))

        # 数据导出为csv
        df.to_excel(save_path + '/data/result_lraspp1.xls')


if __name__ == "__main__":
    # model = torchvision.models.segmentation.fcn_resnet101(pretrained=True)
    # model.eval()
    # model = torch.load('r50_1x.pth', map_location=torch.device('cpu'))
    # pred = model.predict('./image/000000002087.jpg')
    model = models.segmentation.lraspp_mobilenet_v3_large(pretrained=True)
    model.eval()
    save_path = '../analysis/adversarial_attack'
    # handle_image('./image', model)
    handle_image('D:/practise/SafeCV-segment-dlab/data/test2014', model, save_path)
    # model = models.vgg16(pretrained=False)
    # model.load_state_dict(torch.load('./best_fcn.pt'))
    # handle_image('./data/test2017', model)

