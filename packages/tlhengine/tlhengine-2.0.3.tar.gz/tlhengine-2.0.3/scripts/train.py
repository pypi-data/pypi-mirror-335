

import torch
import matplotlib.pyplot as plt

import numpy as np

from tlhengine.engine import Trainer
from tlhengine.models1 import DeepLabV3
from tlhengine.loss import get_segmentation_loss
from tlhengine.datasets.voc import VOCSegmentation, get_voc_aug, get_voc, get_voc_aug_kaggle
from torch import optim
from torch.utils.data import DataLoader, DistributedSampler
from torchvision import transforms

from torch.distributed import init_process_group
from torch import distributed as dist
import os
import platform

from tlhengine.resnetv1_b import resnet50_v1b
from torch import nn

import argparse
def ddp_setup():
    init_process_group(backend="nccl")
    torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))
def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--epochs', type=int, default=150)
    parser.add_argument('--custom-backbone', action='store_true')
    parser.add_argument('--val-freq', type=int, default=10)
    parser.add_argument('--subset', action='store_true')
    parser.add_argument('--subset-size', type=int, default=16)
    parser.add_argument('--aug', action='store_true')
    parser.add_argument('--data-root', type=str, default='/content/data/vocaug/dataset/')
    parser.add_argument('--split-file', type=str, default=None)
    parser.add_argument('--kaggle-aug', action='store_true')

    args = parser.parse_args()
    return args

def main():
    dist_mode = int(os.environ["WORLD_SIZE"]) > 1
    if dist_mode:
        ddp_setup()
    args = get_args()
    print("device:")
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        for i in range(device_count):
            print(torch.cuda.get_device_name(0))
    else:
        print('not cuda')

    print("WORLDSIZE: ", int(os.environ["WORLD_SIZE"]))
    model_kwargs = {}
    if dist_mode:
        model_kwargs['norm_layer'] = nn.SyncBatchNorm
    model = DeepLabV3(21, custom_backbone=args.custom_backbone, **model_kwargs)
    
    criterion = get_segmentation_loss('deeplabv3', aux=False)
    optimizer = 'adam'
    lr = 1e-3

    # image transform
    input_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
    ])

    data_kwargs = {'transform': input_transform}
    # if args.split_file:
    #     data_kwargs['split_file'] = args.split_file
    # data_root = '/kaggle/input/pascal-voc-2012/'
    # if platform.system() == 'Darwin':
    #     data_root='~/code/datasets/voc'
    
    if args.kaggle_aug:
        train_set, val_set = get_voc_aug_kaggle(data_root=args.data_root, **data_kwargs)
    elif args.aug:
        train_set, val_set = get_voc_aug(data_root=args.data_root,**data_kwargs)
    else:
        train_set, val_set = get_voc(data_root=args.data_root,**data_kwargs)
       
    if args.subset:
        train_set = train_set.subset(args.subset_size)
        val_set = val_set.subset(args.subset_size)
    batch_size = args.batch_size
    train_loader = DataLoader(train_set, shuffle=False if dist_mode else True,
                            sampler=DistributedSampler(train_set) if dist_mode else None,
                               batch_size=batch_size)
    val_loader = DataLoader(val_set, batch_size=batch_size)

    trainer = Trainer(model, criterion, optimizer, lr=lr, dist_mode=dist_mode)
    trainer.train(train_loader, val_loader, epochs=args.epochs)
    trainer.evaluate(train_loader)

    trainer.plot_loss()

if __name__ == '__main__':
    main()
    print("done")
