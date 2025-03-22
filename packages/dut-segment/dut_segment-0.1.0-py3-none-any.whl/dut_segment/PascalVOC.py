# 加载模型
from statistics import mean

import cv2
import numpy as np
import onnxruntime
import torchvision
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from torch.nn import functional as F


# import ssl

# 指定颜色编码：一共21类，每一类对应一个颜色编码
# label_colors = np.array([
#     (0, 0, 0),
#     (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
#     (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
#     (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
#     (0, 64, 64), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)
# ])


# 将像素值的每个预测类别分别编码为不同的颜色，然后将图像可视化
def decode_segmaps(image, label_colors, nc=21):
    # 函数将输出的2D图像，会将不同类编码为不同的颜色
    r = np.zeros_like(image).astype(np.uint8)
    g = np.zeros_like(image).astype(np.uint8)
    b = np.zeros_like(image).astype(np.uint8)
    # print(r.shape, g.shape, b.shape)  # (298, 500) (298, 500) (298, 500)

    # 循环遍历每一层(一共21层)，当第cls类出现在image的某些像素值时，这些点索引为idx
    for cls in range(0, nc):
        idx = (image == cls)
        # print("cls:{}, idx.shape:{}".format(cls, idx.shape))

        # 构造rgb三通道：本来是一个类别点变成一个像素(3通道)
        r[idx] = label_colors[cls][0]
        g[idx] = label_colors[cls][1]
        b[idx] = label_colors[cls][2]

    # 三个通道拼接获取彩色图像
    rgbimage = np.stack([r, g, b], axis=2)

    return rgbimage


def get_unique_numbers(array):
    unique_numbers = set()
    for row in array:
        for num in row:
            unique_numbers.add(num)
    return list(unique_numbers)


def seg_output(model, image):

    # 对图像进行变换
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    c_image = image.copy()
    image_t = transform(c_image)

    # 增维
    image_t = image_t.unsqueeze(0)
    pred = model(image_t)
    # pred['out'].shape, pred['aux'].shape
    # (torch.Size([1, 21, 298, 500]), torch.Size([1, 21, 298, 500]))

    # 获取像素点值并降维
    output = pred['out'].squeeze()
    # print(output)
    # print(output.size())

    outputarg = torch.argmax(output, dim=0).numpy()
    # print(outputarg)
    # for i in range(outputarg.shape[0]):
    #     print("预测类别：", outputarg[i], i)
    return outputarg


def compute_seg_iou(seg1, seg2):
    classes1 = np.unique(seg1)  # 获取seg1中的类别
    classes2 = np.unique(seg2)  # 获取seg2中的类别
    # print(classes1, classes2)
    classes = np.union1d(classes1, classes2)  # 合并两个分割图中的类别
    classes = classes[classes != 0]  # 去掉背景标签0
    iou_per_class = []
    weights = []

    for class_id in classes:
        seg1_class = seg1 == class_id
        seg2_class = seg2 == class_id
        # print(seg1_class, seg2_class)
        intersection = np.logical_and(seg1_class, seg2_class)
        union = np.logical_or(seg1_class, seg2_class)

        intersection_count = np.sum(intersection)
        union_count = np.sum(union)

        if union_count == 0:
            iou = 0.0
        else:
            iou = intersection_count / union_count

        iou_per_class.append(iou)
        weights.append(np.sum(seg1_class))  # 使用seg1_class的像素数量作为权重

    weights = np.array(weights)
    weighted_iou = np.sum(np.array(iou_per_class) * weights) / np.sum(weights)

    return weighted_iou


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


# 功能： 输入图像路径，输出分割图像
def seg_predict(model, image, label_colors=None):
    if label_colors is None:
        label_colors = np.array([
            (0, 0, 0),
            (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (128, 0, 128),
            (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0), (64, 128, 0),
            (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128), (192, 128, 128),
            (0, 64, 64), (128, 64, 0), (0, 192, 0), (128, 192, 0), (0, 64, 128)
        ])

    # 对图像进行变换
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    c_image = image.copy()
    image_t = transform(c_image)

    # 增维
    image_t = image_t.unsqueeze(0)
    pred = model(image_t)
    # pred['out'].shape, pred['aux'].shape
    # (torch.Size([1, 21, 298, 500]), torch.Size([1, 21, 298, 500]))

    # 获取像素点值并降维
    output = pred['out'].squeeze()
    # print(output)
    # print(output.size())

    # 获取21类中置信度最高的哪一类，作为像素点的类; 从而实现将3维矩阵变换为二维矩阵
    # 现在该二维矩阵中每个取值均代表图像中对应位置像素点的预测类别
    probs = F.softmax(output, dim=0).detach().numpy()
    # print(probs.size())
    probarg = probs.max(axis=0)
    # print(probarg)
    outputarg = torch.argmax(output, dim=0).numpy()
    print(outputarg.shape)
    # for i in range(outputarg.shape[0]):
    #     print("预测类别：", outputarg[i], i)
    #     print("预测置信度：", probarg[i], i)

    # ===================使用onnx文件进行预测=======================
    # resnet_session = onnxruntime.InferenceSession(model)
    # inputs = {resnet_session.get_inputs()[0].name: to_numpy(image_t)}
    # outs = resnet_session.run(None, inputs)[0]
    #
    # out = torch.tensor(outs, dtype=torch.float64)
    # print(out[0])
    # print(out[0].size())
    # probs = F.softmax(out[0], dim=0).detach().numpy()
    # probarg = probs.max(axis=0)
    # outputarg = torch.argmax(out[0], dim=0).numpy()

    pred = get_unique_numbers(outputarg)
    prob_mean = []
    for s in range(len(pred)):
        prob = []
        for i in range(outputarg.shape[0]):
            for j in range(outputarg.shape[1]):
                if pred[s] == outputarg[i][j]:
                    prob.append(probarg[i][j])
        prob_mean.append(mean(prob))

    # print(prob_mean)

    # 类别通道转换成颜色通道，转换成一张rgb图像
    outputting = decode_segmaps(outputarg, label_colors)

    # 绘制图像
    # plt.figure(figsize=(20, 8))
    # plt.subplot(1, 1, 1)
    # plt.imshow(outputting)
    # plt.show()

    return pred, prob_mean, outputting


# 测试
if __name__ == '__main__':
    # 加载模型
    # model = torchvision.models.resnet50(pretrained=True)
    model = torchvision.models.segmentation.fcn_resnet101(pretrained=True)
    model.eval()
    # model = "faster_rcnn.onnx"

    imagepath = './image/img.png'
    imagepath1 = './image/test_image.jpg'
    raw_image1 = cv2.imread(imagepath)
    image_1 = raw_image1[:, :, ::-1]
    raw_image2 = cv2.imread(imagepath1)
    image_2 = raw_image2[:, :, ::-1]
    # pred_1, prob_1, d_image_1 = seg_predict(model, image_1)
    # pred_2, prob_2, d_image_2 = seg_predict(model, image_2)
    # seg_1 = seg_output(model, image_1)
    # seg_2 = seg_output(model, image_2)
    # miou = compute_seg_iou(seg_1, seg_2)
    # print(miou)
    # print(pred_1, prob_1)
    # plt.imshow(d_image_1)
    # plt.show()
# C:\Users\Yueyuan/.cache\torch\hub\checkpoints
