import math
import time
        
import copy
import datetime
import errno
import hashlib
import os
from collections import defaultdict, deque, OrderedDict
from typing import List, Optional, Tuple
import warnings
import matplotlib.pyplot as plt
import torch
import torch.distributed as dist
from torch import default_generator, nn
from torch.utils.data import Subset
from torch import optim
# from torch._utils import _accumulate
from torch.optim.lr_scheduler import _LRScheduler
import numpy as np
import pickle
import sys
import logging
import os
from importlib import reload
import pynvml

try:
    import tensorflow as tf
    print('tensorflow is installed')
except ImportError:
    print('tensorflow is not installed')
    tf = None

import sys


def plot_image(img, ax=None, save_path=None, dpi=100):
    if isinstance(img, str):
        img = Image.open(img)
    if ax is None:
        fig, ax = plt.subplots(figsize=(img.size[0]/100, img.size[1]/100), dpi=dpi)
    ax.imshow(img)
    ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    if save_path is not None:
        plt.savefig(save_path)
    return ax
def select_gpu_with_max_vram():
    """
    set the os environment variable CUDA_VISIBLE_DEVICES to the GPU with the most available VRAM
    return nothing
    """
    # Initialize NVML
    pynvml.nvmlInit()
    
    device_count = pynvml.nvmlDeviceGetCount()
    max_vram = 0
    selected_gpu = 0

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        available_vram = mem_info.free

        if available_vram > max_vram:
            max_vram = available_vram
            selected_gpu = i

    # Shutdown NVML
    pynvml.nvmlShutdown()

    # Set the CUDA_VISIBLE_DEVICES environment variable
    os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_gpu)
    print(f"Selected GPU {selected_gpu} with {max_vram / 1024 ** 2:.2f} MB available VRAM")



logger = logging.getLogger(__name__)
def append_str_to_file(filepath, string):
    with open(filepath, 'a') as f:
        f.write(string)
def is_debugging() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None
global IS_DEBUGGING
IS_DEBUGGING=is_debugging()

def cd_parent():
    """
    go to parent directory relative to the current file
    """

    # Get the current working directory
    current_dir = os.getcwd()

    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)

    # Change the current working directory to the parent directory
    os.chdir(parent_dir)

class outstream_to_file:
    original_stdout = sys.stdout  # Save a reference to the original standard output
    def __init__(self, filepath): 
        self.filepath = filepath
    def __enter__(self):  
        
        f =open(self.filepath, 'w')
        self.f = f
        sys.stdout = f  # Change the standard output to the file we created.
    
    def __exit__(self, exc_type, exc_value, traceback):      
        sys.stdout = self.original_stdout  # Reset the standard output to its original value
        self.f.close()
 
def print2file(obj, filepath):
    # check if the parent dir of the file exists, if not, ask if the user wants to create it
    if not os.path.exists(os.path.dirname(filepath)):
        print(f"Parent directory of {filepath} does not exist.")
        create_dir = input("Do you want to create it? (y/n): ")
        create_dir = create_dir.strip()
        if create_dir.lower() == 'y' or create_dir == '':
            os.makedirs(os.path.dirname(filepath))
        else:
            print("Exiting without writing to file.")
            return
    with open(filepath, 'w') as f:
        print(obj, file=f)
    

def set_debug_mode():
    if not is_debugging():
        return False
    # reload(torch)
    # print('hi debug helloxxxxyyy')
    # make torch show shape by changing its __repr__ method
    print("setting up debug mode")
    normal_repr = torch.Tensor.__repr__
    # torch.Tensor.__repr__ = lambda self: f"{self.shape}"
    torch.Tensor.__repr__ = lambda self: f"{self.shape}_{normal_repr(self)}"
    torch.Tensor.__str__ = normal_repr
    return True

class Hparams(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

def test_logger ():
    logger.info("hello logger")
    logger.warn('hello warn')
    for handler in logger.handlers:
        print(handler.__class__.__name__, ' from ', handler.__class__.__name__)

def save_pickle_with_obj(obj, pkl_file):
    # if parent not exist, create it
    if not os.path.exists(os.path.dirname(pkl_file)):
        os.makedirs(os.path.dirname(pkl_file))
    if not os.path.exists(pkl_file):
        with open(pkl_file, 'wb') as f:
            # check if obj is a function or other
            pickle.dump(obj, f)
            print("dumping obj to ", pkl_file)
    else:
        print("it's already there")
    
def get_pickle_with_func(func, pkl_file, *args, **kwargs):
    """
    This is used for those time consuming data loading operations
    e.g. in few shot learning, generating the meta dataset is time consuming
    using this saved a lot of time, helped me for fast development.
    """
    if not os.path.exists(pkl_file):
        with open(pkl_file, 'wb') as f:
            # check if obj is a function or other
            data = func(*args, **kwargs)
            pickle.dump(data, f)
    else:
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
    return data

def set_weight_decay(
    model: torch.nn.Module,
    weight_decay: float,
    norm_weight_decay: Optional[float] = None,
    norm_classes: Optional[List[type]] = None,
    custom_keys_weight_decay: Optional[List[Tuple[str, float]]] = None,
):
    if not norm_classes:
        norm_classes = [
            torch.nn.modules.batchnorm._BatchNorm,
            torch.nn.LayerNorm,
            torch.nn.GroupNorm,
            torch.nn.modules.instancenorm._InstanceNorm,
            torch.nn.LocalResponseNorm,
        ]
    norm_classes = tuple(norm_classes)

    params = {
        "other": [],
        "norm": [],
    }
    params_weight_decay = {
        "other": weight_decay,
        "norm": norm_weight_decay,
    }
    custom_keys = []
    if custom_keys_weight_decay is not None:
        for key, weight_decay in custom_keys_weight_decay:
            params[key] = []
            params_weight_decay[key] = weight_decay
            custom_keys.append(key)

    def _add_params(module, prefix=""):
        for name, p in module.named_parameters(recurse=False):
            if not p.requires_grad:
                continue
            is_custom_key = False
            for key in custom_keys:
                target_name = f"{prefix}.{name}" if prefix != "" and "." in key else name
                if key == target_name:
                    params[key].append(p)
                    is_custom_key = True
                    break
            if not is_custom_key:
                if norm_weight_decay is not None and isinstance(module, norm_classes):
                    print("adding norm layer set weight decay to 0")
                    params["norm"].append(p)
                else:
                    params["other"].append(p)

        for child_name, child_module in module.named_children():
            child_prefix = f"{prefix}.{child_name}" if prefix != "" else child_name
            _add_params(child_module, prefix=child_prefix)

    _add_params(model)

    param_groups = []
    for key in params:
        if len(params[key]) > 0:
            param_groups.append({"params": params[key], "weight_decay": params_weight_decay[key]})
    return param_groups

class LinearWarmupCosineAnnealingLR(_LRScheduler):
    def __init__(
        self, optimizer, warmup_epochs, max_epochs, warmup_start_factor, eta_min=0
    ):
        self.warmup_epochs = warmup_epochs
        self.max_epochs = max_epochs
        self.warmup_start_lr = warmup_start_factor * \
                                optimizer.param_groups[0]['lr']
        self.eta_min = eta_min
        self.cycle_epochs = max_epochs - warmup_epochs
        super(LinearWarmupCosineAnnealingLR, self).__init__(optimizer)

    def get_lr(self):
        if self.last_epoch < self.warmup_epochs:
            # Linear warmup phase
            alpha = self.last_epoch / self.warmup_epochs
            return [
                self.warmup_start_lr + alpha * (base_lr - self.warmup_start_lr)
                for base_lr in self.base_lrs
            ]
        else:
            # Cosine annealing phase
            progress = (self.last_epoch - self.warmup_epochs) / self.cycle_epochs
            return [
                self.eta_min
                + 0.5 * (base_lr - self.eta_min) * (1 + np.cos(np.pi * progress))
                for base_lr in self.base_lrs
            ]

class AvgMeter(object):
    def __init__(self, name=None, fmt=':f'):
        self.name = name
        self.fmt = fmt
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

@DeprecationWarning
def random_split(dataset, lengths, generator=default_generator):
    r"""
    Randomly split a dataset into non-overlapping new datasets of given lengths.

    If a list of fractions that sum up to 1 is given,
    the lengths will be computed automatically as
    floor(frac * len(dataset)) for each fraction provided.

    After computing the lengths, if there are any remainders, 1 count will be
    distributed in round-robin fashion to the lengths
    until there are no remainders left.

    Optionally fix the generator for reproducible results, e.g.:

    >>> random_split(range(10), [3, 7], generator=torch.Generator().manual_seed(42))
    >>> random_split(range(30), [0.3, 0.3, 0.4], generator=torch.Generator(
    ...   ).manual_seed(42))

    Args:
        dataset (Dataset): Dataset to be split
        lengths (sequence): lengths or fractions of splits to be produced
        generator (Generator): Generator used for the random permutation.
    """
    if math.isclose(sum(lengths), 1) and sum(lengths) <= 1:
        subset_lengths: List[int] = []
        for i, frac in enumerate(lengths):
            if frac < 0 or frac > 1:
                raise ValueError(f"Fraction at index {i} is not between 0 and 1")
            n_items_in_split = int(
                math.floor(len(dataset) * frac)  # type: ignore[arg-type]
            )
            subset_lengths.append(n_items_in_split)
        remainder = len(dataset) - sum(subset_lengths)  # type: ignore[arg-type]
        # add 1 to all the lengths in round-robin fashion until the remainder is 0
        for i in range(remainder):
            idx_to_add_at = i % len(subset_lengths)
            subset_lengths[idx_to_add_at] += 1
        lengths = subset_lengths
        for i, length in enumerate(lengths):
            if length == 0:
                warnings.warn(
                    f"Length of split at index {i} is 0. "
                    f"This might result in an empty dataset."
                )

    # Cannot verify that dataset is Sized
    if sum(lengths) != len(dataset):  # type: ignore[arg-type]
        raise ValueError(
            "Sum of input lengths does not equal the length of the input dataset!"
        )

    indices = randperm(sum(lengths), generator=generator).tolist()  # type: ignore[call-overload]
    return [
        Subset(dataset, indices[offset - length : offset])
        for offset, length in zip(_accumulate(lengths), lengths)
    ]


def copy_parameters(source_dict, target_dict):
    for (source_name, source_param), (target_name, target_param) in zip(source_dict, target_dict):
        if source_param.data.size() == target_param.data.size():
            target_param.data.copy_(source_param.data)
        else:
            print(f"Warning: Skipping parameter copy due to incompatible sizes - Source: {source_param.data.size()}, Target: {target_param.data.size()}, Name: {source_name}")
def copy_dict2model(source_dict, target_model):
    # Iterate through the saved state_dict and match keys with the new_model's state_dict
    incompatible_keys = []
    for key, value in source_dict.items():
        if key in target_model.state_dict():
            target_model.state_dict()[key].copy_(value)
        else:
            incompatible_keys.append(key)
    if incompatible_keys:
        print(f'incompatible_keys: \n {incompatible_keys}')
def copy_state_dict_with_prefix(src_state_dict, target_model, src_prefix='', target_prefix=''):
    """
    Copy state dictionary parameters from the source model to the target model
    with different prefix conventions.

    Args:
        src_state_dict (dict): State dictionary of the source model.
        target_model (nn.Module): Target model.
        src_prefix (str): Prefix used in the source model.
        target_prefix (str): Prefix used in the target model.

    Returns:
        None
    """
    # Create a new state dictionary for the target model
    new_state_dict = {}

    # Iterate through the source state dictionary
    for key, value in src_state_dict.items():
        # Remove the source prefix if it exists
        if key.startswith(src_prefix):
            new_key = key[len(src_prefix):]
        else:
            new_key = key

        # Add the target prefix and set the parameter in the new state dictionary
        new_key = target_prefix + new_key
        new_state_dict[new_key] = value

    # Load the modified state dictionary into the target model
    target_model.load_state_dict(new_state_dict)
    
    # TODO use copy model to make this more general . 
    # copy_model(target_model, sr)
                

def copy_model(source_model, target_model):

    for (source_name, source_param), (target_name, target_param) in zip(source_model.named_parameters(), target_model.named_parameters()):
        if source_param.data.size() == target_param.data.size():
            target_param.data.copy_(source_param.data)
        else:
            print(f"Warning: Skipping parameter copy due to incompatible sizes - Source: {source_param.data.size()}, Target: {target_param.data.size()}, Name: {source_name}")
            
            
class Timer:
    def __init__(self, name) -> None:
        self.name = name
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time
        print(f"Elapsed time for {self.name}: {self.execution_time:.4f} seconds")
        
    @property
    def excution_time(self):
        return self.execution_time
    
    @property
    def excution_hour_min(self):
        return str(datetime.timedelta(seconds=int(self.execution_time)))

class SmoothedValue:
    """Track a series of values and provide access to smoothed values over a
    window or the global series average.
    """

    def __init__(self, window_size=20, fmt=None):
        if fmt is None:
            fmt = "{median:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)
        self.total = 0.0
        self.count = 0
        self.fmt = fmt

    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n

    def synchronize_between_processes(self):
        """
        Warning: does not synchronize the deque!
        """
        t = reduce_across_processes([self.count, self.total])
        t = t.tolist()
        self.count = int(t[0])
        self.total = t[1]

    @property
    def median(self):
        d = torch.tensor(list(self.deque))
        return d.median().item()

    @property
    def avg(self):
        d = torch.tensor(list(self.deque), dtype=torch.float32)
        return d.mean().item()

    @property
    def global_avg(self):
        return self.total / self.count

    @property
    def max(self):
        return max(self.deque)

    @property
    def value(self):
        return self.deque[-1]

    def __str__(self):
        return self.fmt.format(
            median=self.median, avg=self.avg, global_avg=self.global_avg, max=self.max, value=self.value
        )


class MetricLogger:
    def __init__(self, delimiter="\t"):
        self.meters = defaultdict(SmoothedValue)
        self.delimiter = delimiter

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, torch.Tensor):
                v = v.item()
            assert isinstance(v, (float, int))
            self.meters[k].update(v)

    def __getattr__(self, attr):
        if attr in self.meters:
            return self.meters[attr]
        if attr in self.__dict__:
            return self.__dict__[attr]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")

    def __str__(self):
        loss_str = []
        for name, meter in self.meters.items():
            loss_str.append(f"{name}: {str(meter)}")
        return self.delimiter.join(loss_str)

    def synchronize_between_processes(self):
        for meter in self.meters.values():
            meter.synchronize_between_processes()

    def add_meter(self, name, meter):
        self.meters[name] = meter

    def log_every(self, iterable, print_freq, header=None):
        i = 0
        if not header:
            header = ""
        start_time = time.time()
        end = time.time()
        iter_time = SmoothedValue(fmt="{avg:.4f}")
        data_time = SmoothedValue(fmt="{avg:.4f}")
        space_fmt = ":" + str(len(str(len(iterable)))) + "d"
        if torch.cuda.is_available():
            log_msg = self.delimiter.join(
                [
                    header,
                    "[{0" + space_fmt + "}/{1}]",
                    "eta: {eta}",
                    "{meters}",
                    "time: {time}",
                    "data: {data}",
                    "max mem: {memory:.0f}",
                ]
            )
        else:
            log_msg = self.delimiter.join(
                [header, "[{0" + space_fmt + "}/{1}]", "eta: {eta}", "{meters}", "time: {time}", "data: {data}"]
            )
        MB = 1024.0 * 1024.0
        for obj in iterable:
            data_time.update(time.time() - end)
            yield obj
            iter_time.update(time.time() - end)
            if i % print_freq == 0:
                eta_seconds = iter_time.global_avg * (len(iterable) - i)
                eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
                if torch.cuda.is_available():
                    print(
                        log_msg.format(
                            i,
                            len(iterable),
                            eta=eta_string,
                            meters=str(self),
                            time=str(iter_time),
                            data=str(data_time),
                            memory=torch.cuda.max_memory_allocated() / MB,
                        )
                    )
                else:
                    print(
                        log_msg.format(
                            i, len(iterable), eta=eta_string, meters=str(self), time=str(iter_time), data=str(data_time)
                        )
                    )
            i += 1
            end = time.time()
        total_time = time.time() - start_time
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))
        print(f"{header} Total time: {total_time_str}")


class ExponentialMovingAverage(torch.optim.swa_utils.AveragedModel):
    """Maintains moving averages of model parameters using an exponential decay.
    ``ema_avg = decay * avg_model_param + (1 - decay) * model_param``
    `torch.optim.swa_utils.AveragedModel <https://pytorch.org/docs/stable/optim.html#custom-averaging-strategies>`_
    is used to compute the EMA.
    """

    def __init__(self, model, decay, device="cpu"):
        def ema_avg(avg_model_param, model_param, num_averaged):
            return decay * avg_model_param + (1 - decay) * model_param

        super().__init__(model, device, ema_avg, use_buffers=True)


def accuracy(output, target, topk=(1,)):
    """Computes the accuracy over the k top predictions for the specified values of k"""
    with torch.inference_mode():
        maxk = max(topk)
        batch_size = target.size(0)
        if target.ndim == 2:
            target = target.max(dim=1)[1]

        _, pred = output.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target[None])

        res = []
        for k in topk:
            correct_k = correct[:k].flatten().sum(dtype=torch.float32)
            res.append(correct_k * (100.0 / batch_size))
        return res


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def setup_for_distributed(is_master):
    """
    This function disables printing when not in master process
    """
    import builtins as __builtin__

    builtin_print = __builtin__.print

    def print(*args, **kwargs):
        force = kwargs.pop("force", False)
        if is_master or force:
            builtin_print(*args, **kwargs)

    __builtin__.print = print


def is_dist_avail_and_initialized():
    if not dist.is_available():
        return False
    if not dist.is_initialized():
        return False
    return True


def get_world_size():
    if not is_dist_avail_and_initialized():
        return 1
    return dist.get_world_size()


def get_rank():
    if not is_dist_avail_and_initialized():
        return 0
    return dist.get_rank()


def is_main_process():
    return get_rank() == 0


def save_on_master(*args, **kwargs):
    if is_main_process():
        torch.save(*args, **kwargs)


def init_distributed_mode(args):
    if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
        args.rank = int(os.environ["RANK"])
        args.world_size = int(os.environ["WORLD_SIZE"])
        args.gpu = int(os.environ["LOCAL_RANK"])
    elif "SLURM_PROCID" in os.environ:
        args.rank = int(os.environ["SLURM_PROCID"])
        args.gpu = args.rank % torch.cuda.device_count()
    elif hasattr(args, "rank"):
        pass
    else:
        print("Not using distributed mode")
        args.distributed = False
        return

    args.distributed = True

    torch.cuda.set_device(args.gpu)
    args.dist_backend = "nccl"
    print(f"| distributed init (rank {args.rank}): {args.dist_url}", flush=True)
    torch.distributed.init_process_group(
        backend=args.dist_backend, init_method=args.dist_url, world_size=args.world_size, rank=args.rank
    )
    torch.distributed.barrier()
    setup_for_distributed(args.rank == 0)


def average_checkpoints(inputs):
    """Loads checkpoints from inputs and returns a model with averaged weights. Original implementation taken from:
    https://github.com/pytorch/fairseq/blob/a48f235636557b8d3bc4922a6fa90f3a0fa57955/scripts/average_checkpoints.py#L16

    Args:
      inputs (List[str]): An iterable of string paths of checkpoints to load from.
    Returns:
      A dict of string keys mapping to various values. The 'model' key
      from the returned dict should correspond to an OrderedDict mapping
      string parameter names to torch Tensors.
    """
    params_dict = OrderedDict()
    params_keys = None
    new_state = None
    num_models = len(inputs)
    for fpath in inputs:
        with open(fpath, "rb") as f:
            state = torch.load(
                f,
                map_location=(lambda s, _: torch.serialization.default_restore_location(s, "cpu")),
            )
        # Copies over the settings from the first checkpoint
        if new_state is None:
            new_state = state
        model_params = state["model"]
        model_params_keys = list(model_params.keys())
        if params_keys is None:
            params_keys = model_params_keys
        elif params_keys != model_params_keys:
            raise KeyError(
                f"For checkpoint {f}, expected list of params: {params_keys}, but found: {model_params_keys}"
            )
        for k in params_keys:
            p = model_params[k]
            if isinstance(p, torch.HalfTensor):
                p = p.float()
            if k not in params_dict:
                params_dict[k] = p.clone()
                # NOTE: clone() is needed in case of p is a shared parameter
            else:
                params_dict[k] += p
    averaged_params = OrderedDict()
    for k, v in params_dict.items():
        averaged_params[k] = v
        if averaged_params[k].is_floating_point():
            averaged_params[k].div_(num_models)
        else:
            averaged_params[k] //= num_models
    new_state["model"] = averaged_params
    return new_state


def store_model_weights(model, checkpoint_path, checkpoint_key="model", strict=True):
    """
    This method can be used to prepare weights files for new models. It receives as
    input a model architecture and a checkpoint from the training script and produces
    a file with the weights ready for release.

    Examples:
        from torchvision import models as M

        # Classification
        model = M.mobilenet_v3_large(weights=None)
        print(store_model_weights(model, './class.pth'))

        # Quantized Classification
        model = M.quantization.mobilenet_v3_large(weights=None, quantize=False)
        model.fuse_model(is_qat=True)
        model.qconfig = torch.ao.quantization.get_default_qat_qconfig('qnnpack')
        _ = torch.ao.quantization.prepare_qat(model, inplace=True)
        print(store_model_weights(model, './qat.pth'))

        # Object Detection
        model = M.detection.fasterrcnn_mobilenet_v3_large_fpn(weights=None, weights_backbone=None)
        print(store_model_weights(model, './obj.pth'))

        # Segmentation
        model = M.segmentation.deeplabv3_mobilenet_v3_large(weights=None, weights_backbone=None, aux_loss=True)
        print(store_model_weights(model, './segm.pth', strict=False))

    Args:
        model (pytorch.nn.Module): The model on which the weights will be loaded for validation purposes.
        checkpoint_path (str): The path of the checkpoint we will load.
        checkpoint_key (str, optional): The key of the checkpoint where the model weights are stored.
            Default: "model".
        strict (bool): whether to strictly enforce that the keys
            in :attr:`state_dict` match the keys returned by this module's
            :meth:`~torch.nn.Module.state_dict` function. Default: ``True``

    Returns:
        output_path (str): The location where the weights are saved.
    """
    # Store the new model next to the checkpoint_path
    checkpoint_path = os.path.abspath(checkpoint_path)
    output_dir = os.path.dirname(checkpoint_path)

    # Deep copy to avoid side effects on the model object.
    model = copy.deepcopy(model)
    checkpoint = torch.load(checkpoint_path, map_location="cpu")

    # Load the weights to the model to validate that everything works
    # and remove unnecessary weights (such as auxiliaries, etc.)
    if checkpoint_key == "model_ema":
        del checkpoint[checkpoint_key]["n_averaged"]
        torch.nn.modules.utils.consume_prefix_in_state_dict_if_present(checkpoint[checkpoint_key], "module.")
    model.load_state_dict(checkpoint[checkpoint_key], strict=strict)

    tmp_path = os.path.join(output_dir, str(model.__hash__()))
    torch.save(model.state_dict(), tmp_path)

    sha256_hash = hashlib.sha256()
    with open(tmp_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        hh = sha256_hash.hexdigest()

    output_path = os.path.join(output_dir, "weights-" + str(hh[:8]) + ".pth")
    os.replace(tmp_path, output_path)

    return output_path


def reduce_across_processes(val):
    if not is_dist_avail_and_initialized():
        # nothing to sync, but we still convert to tensor for consistency with the distributed case.
        return torch.tensor(val)

    t = torch.tensor(val, device="cuda")
    dist.barrier()
    dist.all_reduce(t)
    return t



if __name__ == '__main__':
    print('done')