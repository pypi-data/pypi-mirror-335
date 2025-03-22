import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from utils import xZero
# --------------------搭建网络--------------------------------


class SeparableConv2d(nn.Module):  # Depth wise separable conv
    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1, padding=0, dilation=1, bias=False):
        # 每个input channel被自己的filters卷积操作
        super(SeparableConv2d, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, in_channels, kernel_size,
                               stride, padding, dilation, groups=in_channels, bias=bias)
        self.pointwise = nn.Conv2d(
            in_channels, out_channels, 1, 1, 0, 1, 1, bias=bias)

    def forward(self, x):
        x = self.conv1(x)
        x = self.pointwise(x)
        return x


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # in_channels,out_channels,kernel_size,stride(default:1),padding(default:0)
        self.conv1 = torch.nn.Sequential(
            SeparableConv2d(103, 16, 1, 1, 0),  # 1*1卷积核
            nn.ReLU(inplace=True),
            nn.GroupNorm(16, 16)
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(103, 256, 1, 1, 0),
            nn.GroupNorm(256, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            SeparableConv2d(256, 256, 3, 1, 1),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            SeparableConv2d(256, 128, 3, 1, 1),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            SeparableConv2d(128, 64, 3, 1, 1),
            nn.ReLU(inplace=True),
            nn.GroupNorm(64, 64)
        )

        self.classifier = nn.Sequential(
            nn.Linear(80*17*17, 2048),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(2048, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 16),
            nn.LogSoftmax(dim=1)
        )

    def forward(self, x):
        x0 = xZero(x)
        x1 = self.conv1(x0)
        x2 = self.conv2(x)
        x12 = torch.cat((x1, x2), 1)
        xCat = x12.view(-1, self.numFeatures(x12))  # 特征映射一维展开
        output = self.classifier(xCat)
        return output

    def numFeatures(self, x):
        size = x.size()[1:]  # 获取卷积图像的h,w,depth
        num = 1
        for s in size:
            num *= s
            # print(s)
        return num

    def init_weights(self):  # 初始化权值
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                torch.nn.init.xavier_normal_(m.weight.data)
                if m.bias is not None:
                    m.bias.data.zero_()
            elif isinstance(m, nn.GroupNorm):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
            elif isinstance(m, nn.Linear):
                torch.nn.init.normal_(m.weight.data, 0, 0.01)
                m.bias.data.zero_()

def predict(model, path):
    print(len(path), path)

    image = cv2.imread(path)
    image = cv2.resize(image, (224, 224))
    predshape = (1, 224, 224, 3)
    im_pred = image.reshape(predshape)
    im_pred = im_pred.astype('float')

    outputs = model(image)
    outputs.detach_()
    _, predicted = torch.max(outputs.data, 1)
    return predicted
    #
    # for i in imgfile:
    #     imgfile1 = i.replace("\\", "/")
    #     img = cv2.imdecode(np.fromfile(imgfile1, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    #     img = cv2.resize(img, (64, 64))  # 是否需要resize取决于新图片格式与训练时的是否一致
    #
    #     tran = transforms.ToTensor()
    #     img = img.reshape((*img.shape, -1))
    #     img = tran(img)
    #
    #     img = img.unsqueeze(0)
    #     outputs, out1 = model(img)  # outputs，out1修改为你的网络的输出
    #     predicted, index = torch.max(out1, 1)
    #     degre = int(index[0])
    #     list = [0, 45, -45, -90, 90, 135, -135, 180]
    #     print(predicted, list[degre])

# class VGG(nn.Module):
#     def __init__(self, features, num_classes=16, init_weights=False):
#         super(VGG, self).__init__()
#         self.features = features
#         self.classifier = nn.Sequential(
#             nn.Dropout(p=0.5),
#             nn.Linear(512*7*7, 2048),
#             nn.ReLU(True),
#             nn.Dropout(p=0.5),
#             nn.Linear(2048, 2048),
#             nn.ReLU(True),
#             nn.Linear(2048, num_classes)
#         )
#         if init_weights:
#             self._initialize_weights()
 
#     def forward(self, x):
#         # N x 3 x 224 x 224
#         x = self.features(x)
#         # N x 512 x 7 x 7
#         x = torch.flatten(x, start_dim=1)
#         # N x 512*7*7
#         x = self.classifier(x)
#         return x

#     def _initialize_weights(self):
#         for m in self.modules():  # 遍历网络的每一个字模块
#             if isinstance(m, nn.Conv2d):
#                 # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
#                 nn.init.xavier_uniform_(m.weight)  # 初始化权重参数
#                 if m.bias is not None:  # 如果采用了偏置的话，置为0
#                     nn.init.constant_(m.bias, 0)
#             elif isinstance(m, nn.Linear):
#                 nn.init.xavier_uniform_(m.weight)
#                 # nn.init.normal_(m.weight, 0, 0.01)
#                 nn.init.constant_(m.bias, 0)
 
# def make_features(cfg: list):  # 注意这里是 用一个函数把卷积层和池化层堆叠到layers中
#     layers = []
#     in_channels = 3
#     for v in cfg:
#         if v == "M":
#             layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
#         else:
#             conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
#             layers += [conv2d, nn.ReLU(True)]
#             in_channels = v
#     return nn.Sequential(*layers)
# cfgs = { # 论文中的A B D E
#     'vgg11': [64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
#     'vgg13': [64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
#     'vgg16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
#     'vgg19': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
# }
# def vgg(model_name="vgg16", **kwargs):
#     try:
#         cfg = cfgs[model_name]
#     except:
#         print("Warning: model number {} not in cfgs dict!".format(model_name))
#         exit(-1)
#     model = VGG(make_features(cfg), **kwargs)
#     return model
