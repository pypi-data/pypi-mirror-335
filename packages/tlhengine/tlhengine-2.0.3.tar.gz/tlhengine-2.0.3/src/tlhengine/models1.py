import torch
import torchvision

from torchvision import models, datasets, transforms as T
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader, Subset, random_split
from torch.nn import functional as F

import matplotlib as mpl
from matplotlib import pyplot as plt

import os
import sys

from tqdm import tqdm
import time

from PIL import Image
from tlhengine.segbase import SegBaseModel



class ModifiedResNet18(models.ResNet):
    def __init__(self, num_classes=10, stem_stride=1):
        super(ModifiedResNet18, self).__init__(
            block=models.resnet.BasicBlock, layers=[2, 2, 2, 2], num_classes=num_classes)
        if stem_stride == 1:
            self._modify_stem_layer()

    def _modify_stem_layer(self):
        # Resize input from 224x224 to 32x32
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3,
                               stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor):

        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x


class CRB(nn.Sequential):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=False) -> None:
        super().__init__()

        self.add_module('conv', nn.Conv2d(in_channels, out_channels, kernel_size, stride,
                                          padding, dilation=dilation, groups=groups, bias=bias))
        self.add_module('relu', nn.ReLU())
        self.add_module('bn', nn.BatchNorm2d(out_channels))


class CB(nn.Sequential):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=False) -> None:
        super().__init__()

        self.add_module('conv', nn.Conv2d(in_channels, out_channels, kernel_size, stride,
                                          padding, dilation=dilation, groups=groups, bias=bias))
        self.add_module('bn', nn.BatchNorm2d(out_channels))


class SB(nn.Sequential):
    # separableconv and batchnorm
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1, dilation=1, bias=False) -> None:
        super().__init__()
        self.add_module('pw', nn.Conv2d(in_channels, out_channels, 1))
        self.add_module('dw', nn.Conv2d(out_channels, out_channels, kernel_size, stride,
                                          padding, dilation=dilation, groups=out_channels, bias=bias))
        self.add_module('bn', nn.BatchNorm2d(out_channels))


class XceptionBlock(nn.Module):
    def __init__(self, in_channels, out_channels, n_layers=2, first_activation=True, downsample=True, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if downsample:
            self.identity = CB(in_channels, out_channels, kernel_size=1,stride=2 ,padding=0)
        else:
            self.identity = nn.Identity()
        self.activation = nn.ReLU()
        self.layers = nn.Sequential()
        for layer in range(n_layers):
            if layer == 0 and not first_activation:
                self.layers.add_module(
                    f'layer{layer}', SB(in_channels, out_channels))
            else:
                self.layers.add_module(f'layer{layer}',
                                       nn.Sequential(
                                           self.activation,
                                           SB(in_channels if layer==0 else out_channels, out_channels
                                              )))
        if downsample:
            self.layers.add_module('maxpool',
                nn.MaxPool2d(3, 2, padding=1)
            )
    def forward(self, x):
        side = self.identity(x)
        x = self.layers(x)
        return side + x


class Xception(nn.Module):
    def __init__(self, n_classes, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.activation = nn.ReLU()
        self.n_classes = n_classes
        self.entry = self._get_entry_flow()
        self.middle = self._get_middle_flow()
        self.exit = self._get_exit_flow()

    def forward(self, x):
        x = self.entry(x)
        x = self.middle(x)
        x = self.exit(x)
        return x


    def _get_entry_flow(self):
        return nn.Sequential(
            CB(3, 32, stride=2),
            self.activation,
            CB(32, 64),
            self.activation,
            XceptionBlock(64, 128, first_activation=False ),
            XceptionBlock(128, 256),
            XceptionBlock(256, 728)
        )
    def _get_middle_flow(self, num_blocks=8):
        middle_blocks = nn.Sequential()
        for idx in range(num_blocks):
            middle_blocks.add_module(f'block{idx}', XceptionBlock(728, 728, 3, downsample=False))
        return middle_blocks
    def _get_exit_flow(self):
        return nn.Sequential(
            XceptionBlock(728, 1024 ),
            SB(1024, 1536),
            self.activation,
            SB(1536, 2048),
            self.activation,
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(2048, self.n_classes)
        )

class DeepLabV3(SegBaseModel):
    r"""DeepLabV3

    Parameters
    ----------
    nclass : int
        Number of categories for the training dataset.
    backbone : string
        Pre-trained dilated backbone network type (default:'resnet50'; 'resnet50',
        'resnet101' or 'resnet152').
    norm_layer : object
        Normalization layer used in backbone network (default: :class:`nn.BatchNorm`;
        for Synchronized Cross-GPU BachNormalization).
    aux : bool
        Auxiliary loss.

    Reference:
        Chen, Liang-Chieh, et al. "Rethinking atrous convolution for semantic image segmentation."
        arXiv preprint arXiv:1706.05587 (2017).
    """

    def __init__(self, nclass, backbone='resnet50', aux=False, pretrained_base=True, **kwargs):
        super().__init__(nclass, aux, backbone, pretrained_base=pretrained_base, **kwargs)
        self.num_classes = nclass
        self.head = _DeepLabHead(nclass, **kwargs)
        if self.aux:
            self.auxlayer = _FCNHead(1024, nclass, **kwargs)

        self.__setattr__('exclusive', ['head', 'auxlayer'] if aux else ['head'])

    def forward(self, x):
        size = x.size()[2:]
        _, _, _, c4 = self.base_forward(x)
        outputs = []
        x = self.head(c4)
        x = F.interpolate(x, size, mode='bilinear', align_corners=True)
        outputs.append(x)

        if self.aux:
            auxout = self.auxlayer(c3)
            auxout = F.interpolate(auxout, size, mode='bilinear', align_corners=True)
            outputs.append(auxout)
        return tuple(outputs)


class _DeepLabHead(nn.Module):
    def __init__(self, nclass, norm_layer=nn.BatchNorm2d, norm_kwargs=None, **kwargs):
        super(_DeepLabHead, self).__init__()
        self.aspp = _ASPP(2048, [6, 12, 18], norm_layer=norm_layer, norm_kwargs=norm_kwargs, **kwargs)
        self.block = nn.Sequential(
            nn.Conv2d(256, 256, 3, padding=1, bias=False),
            norm_layer(256, **({} if norm_kwargs is None else norm_kwargs)),
            nn.ReLU(True),
            nn.Dropout(0.1),
            nn.Conv2d(256, nclass, 1)
        )

    def forward(self, x):
        x = self.aspp(x)
        return self.block(x)


class _ASPPConv(nn.Module):
    def __init__(self, in_channels, out_channels, atrous_rate, norm_layer, norm_kwargs):
        super(_ASPPConv, self).__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=atrous_rate, dilation=atrous_rate, bias=False),
            norm_layer(out_channels, **({} if norm_kwargs is None else norm_kwargs)),
            nn.ReLU(True)
        )

    def forward(self, x):
        return self.block(x)


class _AsppPooling(nn.Module):
    def __init__(self, in_channels, out_channels, norm_layer, norm_kwargs, **kwargs):
        super(_AsppPooling, self).__init__()
        self.gap = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            norm_layer(out_channels, **({} if norm_kwargs is None else norm_kwargs)),
            nn.ReLU(True)
        )

    def forward(self, x):
        size = x.size()[2:]
        pool = self.gap(x)
        out = F.interpolate(pool, size, mode='bilinear', align_corners=True)
        return out


class _ASPP(nn.Module):
    def __init__(self, in_channels, atrous_rates, norm_layer, norm_kwargs, **kwargs):
        super(_ASPP, self).__init__()
        out_channels = 256
        self.b0 = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            norm_layer(out_channels, **({} if norm_kwargs is None else norm_kwargs)),
            nn.ReLU(True)
        )

        rate1, rate2, rate3 = tuple(atrous_rates)
        self.b1 = _ASPPConv(in_channels, out_channels, rate1, norm_layer, norm_kwargs)
        self.b2 = _ASPPConv(in_channels, out_channels, rate2, norm_layer, norm_kwargs)
        self.b3 = _ASPPConv(in_channels, out_channels, rate3, norm_layer, norm_kwargs)
        self.b4 = _AsppPooling(in_channels, out_channels, norm_layer=norm_layer, norm_kwargs=norm_kwargs)

        self.project = nn.Sequential(
            nn.Conv2d(5 * out_channels, out_channels, 1, bias=False),
            norm_layer(out_channels, **({} if norm_kwargs is None else norm_kwargs)),
            nn.ReLU(True),
            nn.Dropout(0.5)
        )

    def forward(self, x):
        feat1 = self.b0(x)
        feat2 = self.b1(x)
        feat3 = self.b2(x)
        feat4 = self.b3(x)
        feat5 = self.b4(x)
        x = torch.cat((feat1, feat2, feat3, feat4, feat5), dim=1)
        x = self.project(x)
        return x

def main():
    # model =  Xception(6)
    model = DeepLabV3(20)
    print(model)
    x = torch.rand(2, 3, 448, 448)
    out = model(x)
    print(len(out))
    print(out[0].shape)
    print(model(x).shape)

if __name__ == '__main__':
    main()