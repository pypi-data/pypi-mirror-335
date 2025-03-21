import torch
import numpy as np


class CosineWarmupScheduler(torch.optim.lr_scheduler._LRScheduler):
    def __init__(self, optimizer, warmup, max_iters, min_percent=0.01):
        self.warmup = warmup
        self.max_num_iters = max_iters
        self.min_percent = min_percent
        super().__init__(optimizer)

    def get_lr(self):
        lr_factor = self.get_lr_factor(epoch=self.last_epoch)
        return [base_lr * lr_factor for base_lr in self.base_lrs]

    def get_lr_factor(self, epoch):
        lr_factor = 0.5 * (1 + np.cos(np.pi * epoch / self.max_num_iters))
        if epoch <= self.warmup:
            lr_factor *= epoch * 1.0 / self.warmup
        else:
            lr_factor = max(lr_factor, self.min_percent)
        return lr_factor


class LinearWarmupScheduler(torch.optim.lr_scheduler._LRScheduler):
    def __init__(self, optimizer, warmup, max_iters, min_percent=0.01):
        self.warmup = warmup
        self.max_num_iters = max_iters
        self.min_percent = min_percent
        super().__init__(optimizer)

    def get_lr(self):
        lr_factor = self.get_lr_factor(epoch=self.last_epoch)
        return [base_lr * lr_factor for base_lr in self.base_lrs]

    def get_lr_factor(self, epoch):
        if epoch <= self.warmup:
            lr_factor = max(epoch * 1.0 / self.warmup, self.min_percent)
        else:
            lr_factor = max(
                1 - ((epoch - self.warmup) * 1.0 / self.max_num_iters), self.min_percent
            )

        return lr_factor
