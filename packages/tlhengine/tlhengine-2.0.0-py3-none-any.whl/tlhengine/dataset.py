from torchvision import models, datasets
from torch.utils.data import DataLoader, Dataset, Subset, random_split
import torch
import os
from PIL import Image
from torchvision import transforms as T
import logging

logger = logging.getLogger('training_logger')

class ImageDataset(torch.utils.data.Dataset):
    def __init__(self, root, transform=None):
        self.root = root
        self.transform = transform
        self.images = os.listdir(root)

    def __getitem__(self, index):
        image_path = os.path.join(self.root, self.images[index])
        image = Image.open(image_path).convert('RGB')

        if self.transform is not None:
            image = self.transform(image)

        return image

    def __len__(self):
        return len(self.images)
    


class CatDogDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.file_list = [file for file in os.listdir(root_dir) if file.startswith("cat") or file.startswith("dog")]

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        img_name = os.path.join(self.root_dir, self.file_list[idx])
        image = Image.open(img_name).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
        
        label = 0 if self.file_list[idx].startswith("cat") else 1
        
        return image, label

def get_cifar10(data_root = '~/data/', use_full=False, batch_size=16):
    
    data_root = os.path.expanduser(data_root)
    logger.info(f'data_root is of type {type(data_root)} ,value is {data_root}')
    train_transforms = T.Compose([
        # T.Resize(224),
        # T.CenterCrop(224),
        T.ToTensor()
    ])

    test_transforms = train_transforms


    traindataset_full= datasets.CIFAR10(
        data_root,
        download=True,
        transform=train_transforms,
        train= True
    )

    testdataset_full = datasets.CIFAR10(
        data_root,
        download=True,
        transform=test_transforms,
        train= False
    )

    if use_full:

        train_loader = DataLoader(traindataset_full, batch_size = batch_size, shuffle=True, num_workers=4)
        test_loader = DataLoader(testdataset_full, batch_size = batch_size, shuffle=False, num_workers=4)

    else:
        subset_factor = 0.1
        traindataset = Subset(traindataset_full, range(int(subset_factor * len(traindataset_full))))
        testdataset = Subset(testdataset_full, range(int(subset_factor * len(testdataset_full))))

        train_loader = DataLoader(traindataset, batch_size = batch_size, shuffle=True, num_workers=4)
        test_loader = DataLoader(testdataset, batch_size = batch_size, shuffle=False, num_workers=4)

    return train_loader, test_loader


def get_catdog(batch_size = 16, train_factor=0.8):
    root_dir = '~/code/datasets/dogcat'
    root_dir = os.path.expanduser(root_dir)
    train_dir = os.path.join(root_dir, 'train')
    test_dir = os.path.join(root_dir, 'test1')
    train_transforms = T.Compose([
        T.RandomResizedCrop(224,),
        T.ToTensor()
    ])
    test_transforms = T.Compose([
        T.CenterCrop(224),
        T.ToTensor()
    ])
    labeled_dataset = datasets.ImageFolder(
        train_dir,
        train_transforms,

    )
    test_dataset = ImageDataset(
        test_dir,
        test_transforms
    )

    train_size = int(train_factor * len(labeled_dataset))
    val_size = len(labeled_dataset) - train_size
    train_dataset, val_dataset = random_split(labeled_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, persistent_workers=True)

    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4, persistent_workers=True)

    return train_loader, val_loader, test_loader

def get_catdog_kaggle(root_dir = '~/code/datasets/dogcat', batch_size = 16, train_factor=0.8):
    root_dir = os.path.expanduser(root_dir)
    train_dir = os.path.join(root_dir, 'train', 'train')
    test_dir = os.path.join(root_dir, 'test', 'test')
    train_transforms = T.Compose([
        # T.RandomResizedCrop(224,),
        T.Resize(224),
        T.CenterCrop(224),
        T.ToTensor()
    ])
    test_transforms = T.Compose([
        T.CenterCrop(224),
        T.ToTensor()
    ])
    labeled_dataset = CatDogDataset(
        train_dir,
        train_transforms,

    )
    test_dataset = CatDogDataset(
        test_dir,
        test_transforms
    )

    train_size = int(train_factor * len(labeled_dataset))
    val_size = len(labeled_dataset) - train_size
    train_dataset, val_dataset = random_split(labeled_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4, persistent_workers=True)

    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4, persistent_workers=True)

    return train_loader, val_loader, test_loader

def get_other():
    print("get other")

def get_other2():
    print("get other 2")
    