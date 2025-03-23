"""Base Model for Semantic Segmentation"""
import torch.nn as nn
from torchvision import  models
# from .base_models.resnetv1b import resnet50_v1s, resnet101_v1s, resnet152_v1s, resnet50_v1b
from tlhengine.resnetv1_b import resnet50_v1b

__all__ = ['SegBaseModel']


class SegBaseModel(nn.Module):
    r"""Base Model for Semantic Segmentation

    Parameters
    ----------
    backbone : string
        Pre-trained dilated backbone network type (default:'resnet50'; 'resnet50',
        'resnet101' or 'resnet152').
    """

    def __init__(self, nclass, aux, backbone='resnet50', pretrained_base=True, custom_backbone=True, **kwargs):
        super().__init__()
        dilated = True
        self.aux = aux
        self.nclass = nclass
        if backbone == 'resnet50':
            if custom_backbone:
                self.pretrained = resnet50_v1b(pretrained=pretrained_base, **kwargs)
            else:
                self.pretrained = models.resnet50(pretrained=pretrained_base, replace_stride_with_dilation=[False, True,True], **kwargs)
        # elif backbone == 'resnet101':
        #     self.pretrained = resnet101_v1s(pretrained=pretrained_base, dilated=dilated, **kwargs)
        # elif backbone == 'resnet152':
        #     self.pretrained = resnet152_v1s(pretrained=pretrained_base, dilated=dilated, **kwargs)
        # else:
        #     raise RuntimeError('unknown backbone: {}'.format(backbone))


    def base_forward(self, x):
        """forwarding pre-trained network"""
        x = self.pretrained.conv1(x)
        x = self.pretrained.bn1(x)
        x = self.pretrained.relu(x)
        x = self.pretrained.maxpool(x)
        c1 = self.pretrained.layer1(x)
        c2 = self.pretrained.layer2(c1)
        c3 = self.pretrained.layer3(c2)
        c4 = self.pretrained.layer4(c3)


        return c1, c2, c3, c4

    def evaluate(self, x):
        """evaluating network with inputs and targets"""
        return self.forward(x)[0]

    def demo(self, x):
        pred = self.forward(x)
        if self.aux:
            pred = pred[0]
        return pred
