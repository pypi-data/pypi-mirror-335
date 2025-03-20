"""Pascal VOC Semantic Segmentation Dataset."""
import os
import torch
import numpy as np

from PIL import Image
from .segbase import SegmentationDataset
from torch.utils.data import Subset
import scipy.io as sio


class VOCAugSegmentation(SegmentationDataset):
    """Pascal VOC Augmented Semantic Segmentation Dataset.

    Parameters
    ----------
    root : string
        Path to VOCdevkit folder. Default is './datasets/voc'
    split: string
        'train', 'val' or 'test'
    transform : callable, optional
        A function that transforms the image
    Examples
    --------
    >>> from torchvision import transforms
    >>> import torch.utils.data as data
    >>> # Transforms for Normalization
    >>> input_transform = transforms.Compose([
    >>>     transforms.ToTensor(),
    >>>     transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
    >>> ])
    >>> # Create Dataset
    >>> trainset = VOCAugSegmentation(split='train', transform=input_transform)
    >>> # Create Training Loader
    >>> train_data = data.DataLoader(
    >>>     trainset, 4, shuffle=True,
    >>>     num_workers=4)
    """
    NUM_CLASS = 21

    def __init__(self, root='../datasets/vocaug', split='train', mode=None, transform=None, **kwargs):
        super(VOCAugSegmentation, self).__init__(root, split, mode, transform, **kwargs)
        # train/val/test splits are pre-cut
        _voc_root = os.path.expanduser(root)
        _mask_dir = os.path.join(_voc_root, 'cls')
        _image_dir = os.path.join(_voc_root, 'img')
        if split == 'train':
            _split_f = os.path.join(_voc_root, 'train.txt')
        elif split == 'val':
            _split_f = os.path.join(_voc_root, 'val.txt')
        else:
            raise RuntimeError('Unknown dataset split: {}'.format(split))

        self.images = []
        self.masks = []
        with open(os.path.join(_split_f), "r") as lines:
            for line in lines:
                _image = os.path.join(_image_dir, line.rstrip('\n') + ".jpg")
                assert os.path.isfile(_image)
                self.images.append(_image)
                _mask = os.path.join(_mask_dir, line.rstrip('\n') + ".mat")
                assert os.path.isfile(_mask)
                self.masks.append(_mask)

        assert (len(self.images) == len(self.masks))
        print('Found {} images in the folder {}'.format(len(self.images), _voc_root))

    def __getitem__(self, index):
        img = Image.open(self.images[index]).convert('RGB')
        target = self._load_mat(self.masks[index])
        # synchrosized transform
        if self.mode == 'train':
            img, target = self._sync_transform(img, target)
        elif self.mode == 'val':
            img, target = self._val_sync_transform(img, target)
        else:
            raise RuntimeError('unknown mode for dataloader: {}'.format(self.mode))
        # general resize, normalize and toTensor
        if self.transform is not None:
            img = self.transform(img)
        return img, target, os.path.basename(self.images[index])

    def _mask_transform(self, mask):
        return torch.LongTensor(np.array(mask).astype('int32'))

    def _load_mat(self, filename):
        mat = sio.loadmat(filename, mat_dtype=True, squeeze_me=True, struct_as_record=False)
        mask = mat['GTcls'].Segmentation
        return Image.fromarray(mask)

    def __len__(self):
        return len(self.images)

    @property
    def classes(self):
        """Category names."""
        return ('background', 'airplane', 'bicycle', 'bird', 'boat', 'bottle',
                'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse',
                'motorcycle', 'person', 'potted-plant', 'sheep', 'sofa', 'train',
                'tv')

class VOCSegmentationAugKaggle(SegmentationDataset):
    """Pascal VOC Semantic Segmentation Dataset.

    Parameters
    ----------
    root : string
        Path to VOCdevkit folder. Default is './datasets/VOCdevkit'
    split: string
        'train', 'val' or 'test'
    transform : callable, optional
        A function that transforms the image
    Examples
    --------
    >>> from torchvision import transforms
    >>> import torch.utils.data as data
    >>> # Transforms for Normalization
    >>> input_transform = transforms.Compose([
    >>>     transforms.ToTensor(),
    >>>     transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
    >>> ])
    >>> # Create Dataset
    >>> trainset = VOCSegmentation(split='train', transform=input_transform)
    >>> # Create Training Loader
    >>> train_data = data.DataLoader(
    >>>     trainset, 4, shuffle=True,
    >>>     num_workers=4)
    """
    BASE_DIR = 'VOC2012'
    NUM_CLASS = 21

    def __init__(self, root='~/code/datasets/voc', split='train_aug', split_file=None, mode=None, transform=None, **kwargs):
        super().__init__(root, split, mode, transform, **kwargs)
        root = os.path.expanduser(root)
        _voc_root = os.path.join(root, self.BASE_DIR)
        _mask_dir = os.path.join(_voc_root, 'SegmentationClassAug')
        _image_dir = os.path.join(_voc_root, 'JPEGImages')
        # train/val/test splits are pre-cut
        _splits_dir = os.path.join(_voc_root, 'ImageSets/SegmentationAug')
        if split_file:
            _split_f = split_file
        elif split == 'train':
            _split_f = os.path.join(_splits_dir, 'train.txt')
        elif split == 'val':
            _split_f = os.path.join(os.path.join(_voc_root, 'ImageSets/Segmentation'), 'val.txt')
        elif split == 'test':
            _split_f = os.path.join(os.path.join(_voc_root, 'ImageSets/Segmentation'), 'val.txt')
        elif split == 'train_aug':
            _split_f = os.path.join(_splits_dir, 'train_aug.txt')
        else:
            raise RuntimeError('Unknown dataset split.')

        self.images = []
        self.masks = []
        with open(os.path.join(_split_f), "r") as lines:
            for line in lines:
                _image = os.path.join(_image_dir, line.rstrip('\n') + ".jpg")
                assert os.path.isfile(_image)
                self.images.append(_image)
                if split != 'test':
                    _mask = os.path.join(_mask_dir, line.rstrip('\n') + ".png")
                    assert os.path.isfile(_mask), "path: {}, split_f: {}".format(_mask, _split_f)
                    self.masks.append(_mask)

        if split != 'test':
            assert (len(self.images) == len(self.masks))
        print('Found {} images in the folder {}'.format(len(self.images), _voc_root))

    def subset(self, size):
        return Subset(self, range(size))

    def __getitem__(self, index):
        img = Image.open(self.images[index]).convert('RGB')
       
        if self.mode == 'test':
            img = self._img_transform(img)
            if self.transform is not None:
                img = self.transform(img)
            return img, os.path.basename(self.images[index])
        mask = Image.open(self.masks[index])
        # synchronized transform
        if self.mode == 'train':
            img, mask = self._sync_transform(img, mask)
        elif self.mode == 'val':
            img, mask = self._val_sync_transform(img, mask)
        else:
            assert self.mode == 'testval'
            img, mask = self._img_transform(img), self._mask_transform(mask)
        # general resize, normalize and toTensor
        if self.transform is not None:
            img = self.transform(img)

        # return img, mask, os.path.basename(self.images[index])
        return img, mask


    def __len__(self):
        return len(self.images)

    def _mask_transform(self, mask):
        target = np.array(mask).astype('int32')
        target[target == 255] = -1
        return torch.from_numpy(target).long()

    @property
    def classes(self):
        """Category names."""
        return ('background', 'airplane', 'bicycle', 'bird', 'boat', 'bottle',
                'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse',
                'motorcycle', 'person', 'potted-plant', 'sheep', 'sofa', 'train',
                'tv')


class VOCSegmentation(SegmentationDataset):
    """Pascal VOC Semantic Segmentation Dataset.

    Parameters
    ----------
    root : string
        Path to VOCdevkit folder. Default is './datasets/VOCdevkit'
    split: string
        'train', 'val' or 'test'
    transform : callable, optional
        A function that transforms the image
    Examples
    --------
    >>> from torchvision import transforms
    >>> import torch.utils.data as data
    >>> # Transforms for Normalization
    >>> input_transform = transforms.Compose([
    >>>     transforms.ToTensor(),
    >>>     transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
    >>> ])
    >>> # Create Dataset
    >>> trainset = VOCSegmentation(split='train', transform=input_transform)
    >>> # Create Training Loader
    >>> train_data = data.DataLoader(
    >>>     trainset, 4, shuffle=True,
    >>>     num_workers=4)
    """
    BASE_DIR = 'VOC2012'
    NUM_CLASS = 21

    def __init__(self, root='~/code/datasets/voc', split='train', split_file=None, mode=None, transform=None, **kwargs):
        super(VOCSegmentation, self).__init__(root, split, mode, transform, **kwargs)
        root = os.path.expanduser(root)
        _voc_root = os.path.join(root, self.BASE_DIR)
        _mask_dir = os.path.join(_voc_root, 'SegmentationClass')
        _image_dir = os.path.join(_voc_root, 'JPEGImages')
        # train/val/test splits are pre-cut
        _splits_dir = os.path.join(_voc_root, 'ImageSets/Segmentation')
        if split_file:
            _split_f = split_file
        elif split == 'train':
            _split_f = os.path.join(_splits_dir, 'train.txt')
        elif split == 'val':
            _split_f = os.path.join(_splits_dir, 'val.txt')
        elif split == 'test':
            _split_f = os.path.join(_splits_dir, 'test.txt')
        else:
            raise RuntimeError('Unknown dataset split.')

        self.images = []
        self.masks = []
        with open(os.path.join(_split_f), "r") as lines:
            for line in lines:
                _image = os.path.join(_image_dir, line.rstrip('\n') + ".jpg")
                assert os.path.isfile(_image)
                self.images.append(_image)
                if split != 'test':
                    _mask = os.path.join(_mask_dir, line.rstrip('\n') + ".png")
                    assert os.path.isfile(_mask)
                    self.masks.append(_mask)

        if split != 'test':
            assert (len(self.images) == len(self.masks))
        print('Found {} images in the folder {}'.format(len(self.images), _voc_root))

    def subset(self, size):
        return Subset(self, range(size))

    def __getitem__(self, index):
        img = Image.open(self.images[index]).convert('RGB')
       
        if self.mode == 'test':
            img = self._img_transform(img)
            if self.transform is not None:
                img = self.transform(img)
            return img, os.path.basename(self.images[index])
        mask = Image.open(self.masks[index])
        # synchronized transform
        if self.mode == 'train':
            img, mask = self._sync_transform(img, mask)
        elif self.mode == 'val':
            img, mask = self._val_sync_transform(img, mask)
        else:
            assert self.mode == 'testval'
            img, mask = self._img_transform(img), self._mask_transform(mask)
        # general resize, normalize and toTensor
        if self.transform is not None:
            img = self.transform(img)

        # return img, mask, os.path.basename(self.images[index])
        return img, mask


    def __len__(self):
        return len(self.images)

    def _mask_transform(self, mask):
        target = np.array(mask).astype('int32')
        target[target == 255] = -1
        return torch.from_numpy(target).long()

    @property
    def classes(self):
        """Category names."""
        return ('background', 'airplane', 'bicycle', 'bird', 'boat', 'bottle',
                'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse',
                'motorcycle', 'person', 'potted-plant', 'sheep', 'sofa', 'train',
                'tv')

def get_voc_aug(data_root = '../datasets/vocaug', **data_kwargs):
    train_set = VOCAugSegmentation(root=data_root, **data_kwargs)
    val_set = VOCAugSegmentation(root=data_root, split='val', **data_kwargs)
    return train_set, val_set

def get_voc(data_root, **data_kwargs):
    train_set = VOCSegmentation(root=data_root, **data_kwargs)
    val_set = VOCSegmentation(root=data_root, split='val', **data_kwargs)
    return train_set, val_set

def get_voc_aug_kaggle(data_root, **data_kwargs):
    train_set = VOCSegmentationAugKaggle(root=data_root, **data_kwargs)
    val_set = VOCSegmentationAugKaggle(root=data_root, split='val', **data_kwargs)
    return train_set, val_set
if __name__ == '__main__':
    dataset = VOCSegmentation()