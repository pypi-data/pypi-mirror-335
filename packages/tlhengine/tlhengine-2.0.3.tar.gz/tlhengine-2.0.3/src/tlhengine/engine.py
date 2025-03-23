from calendar import c
import torch
import torchvision

from torchvision import models, datasets, transforms as T
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader, Subset, random_split
from torch.cuda.amp import autocast, GradScaler
import torch.backends.cudnn as cudnn
import matplotlib as mpl
from matplotlib import pyplot as plt

import os
import sys

import logging

from tqdm import tqdm
import time
import datetime

from PIL import Image
from tlhengine.scores import SegmentationMetric, MeanMetric, Acc
from tlhengine.models1 import SegBaseModel
from torch.nn.parallel import DistributedDataParallel as DDP


class Trainer:
    def __init__(
        self,
        model,
        criterion,
        optimizer="adam",
        device='auto',
        amp=True,
        lr=1e-2,
        dist_mode=False,
    ):
        self.criterion = criterion
        self.gpu_id = int(os.environ.get("LOCAL_RANK", 0))
        self.loss_history = []
        self.dist_mode = dist_mode
        self.loss_history = []
        self.amp = amp
        # set current data time and a random string as workdir 
        c_time = datetime.datetime.now()
        adjust_time = c_time + datetime.timedelta(hours=8)
        self.workdir = f"runs_{adjust_time.strftime('%Y-%m-%d_%H-%M-%S')}_{os.urandom(8).hex()}/"
        os.mkdir(self.workdir)
        self.setup_logging()
        self.logger.info(f"using amp: {self.amp}")
        self.dist_mode = dist_mode
        if device == 'auto':
            if torch.cuda.is_available():
                self.device = "cuda"
                cudnn.benchmark=True
            elif torch.has_mps:
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        self.device_type = self.device
        self.logger.info(f"Traniner using device {self.device}")
        self.loss_metric = MeanMetric()
        if issubclass(model.__class__, SegBaseModel):
            self.metric = SegmentationMetric(model.num_classes)
        else:
            self.metric = Acc()

        if self.device == "cuda" and dist_mode:
            self.device = self.gpu_id
            self.model = model.to(self.gpu_id)
            self.model = DDP(
                self.model, device_ids=[self.gpu_id], find_unused_parameters=True
            )
        else:
            self.model = model.to(self.device)
            

        # self.logger.info(self.model)
        if optimizer == "adam":
            self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def setup_logging(self):
        self.logger = logging.getLogger("training_logger")
        self.logger.setLevel(logging.DEBUG)

        # Create handlers for both file and console output
        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)

        # File handler
        log_file = self.workdir+ "training.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.INFO)

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def train(
        self, train_loader: DataLoader, val_loader=None, epochs=1, amp=True, val_freq=1
    ):
        self.lr_scheduler = optim.lr_scheduler.PolynomialLR(
            self.optimizer, epochs * len(train_loader), 0.9
        )
        self.model.train()
        self.amp = amp
        scaler = GradScaler() if amp else None
        self.logger.info(f"GPU ID: {self.gpu_id}")
        for epoch in range(1, epochs + 1):
            self.logger.info(f"Epoch {epoch}")
            start_epoch_train_time = time.time()
            self.model.train()
            if self.dist_mode:
                train_loader.sampler.set_epoch(epoch)
            # progress_bar = tqdm(train_loader, total=len(train_loader), leave=True, position=0, ncols=40)
            for batch_idx, batch_data in enumerate(train_loader):
                if len(batch_data) == 2:
                    inputs, labels = batch_data
                elif len(batch_data) == 3:
                    inputs, labels, file_name = batch_data
                else:
                    raise ValueError("batch_data length is wrong")
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                self.optimizer.zero_grad()

                if amp and self.device_type == "cuda":
                    with autocast():
                        outputs = self.model(inputs)
                        loss = self.criterion(outputs, labels)
                        scaler.scale(loss).backward()
                        scaler.step(self.optimizer)
                        scaler.update()
                else:
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, labels)
                    loss.backward()
                    self.optimizer.step()

                self.lr_scheduler.step()
                self.loss_metric.update(loss.item())
                # progress_bar.set_description(f'Loss: {self.loss_metric.get():.4f}, lr: {self.optimizer.param_groups[0]["lr"]:.4f}')
                if batch_idx % 10 == 0:
                    self.logger.info(
                        f"Epoch:{epoch}|({batch_idx+1}/{len(train_loader)})|loss: {loss.item():.4f}, lr: {self.optimizer.param_groups[0]['lr']:.4f}"
                    )
                    self.loss_history.append(loss.item())

            end_epoch_train_time = time.time()
            self.logger.info(
                f"training time is {(end_epoch_train_time - start_epoch_train_time):.2f}s"
            )
            # Evaluate the model after each epoch
            if val_loader and epoch % val_freq == 0:
                val_dict = self.evaluate(val_loader)
                end_epoch_val_time = time.time()
                self.logger.info(
                    f"eval time is {(end_epoch_val_time - end_epoch_train_time):.2f}s"
                )
                # self.logger.info(f"accuracy is {accuracy:.4f}")
        if self.gpu_id == 0 or not self.dist_mode:
            self._save_checkpoint(epoch)
        self.evaluate(train_loader)

    def evaluate(self, test_loader):
        self.model.eval()
        # total_correct = 0
        # total_samples = 0
        self.metric.reset()
        progress_bar = tqdm(test_loader)
        with torch.no_grad():
            for batch_data in progress_bar:
                if len(batch_data) == 2:
                    inputs, labels = batch_data
                elif len(batch_data) == 3:
                    inputs, labels, file_name = batch_data
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                if self.amp and self.device_type == "cuda":
                    with autocast():
                        outputs = self.model(inputs)
                else:
                    outputs = self.model(inputs)

                if type(outputs) == list or type(outputs) == tuple:
                    self.metric.update(outputs[0], labels)
                else:
                    self.metric.update(outputs, labels)

                # _, predicted = torch.max(outputs.data, 1)
                # total_samples += labels.size(0)
                # total_correct += (predicted == labels).sum().item()
                # progress_bar.set_description(f"Correct: {total_correct} / {total_samples}")

        # accuracy = total_correct / total_samples
        self.logger.info(self.metric.__str__())
        return self.metric.get()

    def _save_checkpoint(self, epoch):
        ckp = (
            self.model.module.state_dict()
            if self.dist_mode
            else self.model.state_dict()
        )
        path = self.workdir+ f"/ckp_{epoch}.pth"

        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(ckp, path)
        self.logger.info(f"Saved checkpoint at {path}")

    def predict(self, inputs):
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(inputs)
            _, predicted = torch.max(outputs.data, 1)
        return predicted

    def plot_loss(self):
        mean_loss = sum(self.loss_history) / len(self.loss_history)
        plt.plot(self.loss_history)
        plt.ylim(0, 2 * mean_loss)
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.title("Training Loss")
        plt.show()

    def reset_loss(self):
        self.loss_history = []
