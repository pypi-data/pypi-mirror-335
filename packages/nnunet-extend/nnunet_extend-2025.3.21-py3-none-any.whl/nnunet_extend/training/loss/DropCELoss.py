import torch
from torch import nn, Tensor
from nnunetv2.training.loss.compound_losses import DC_and_CE_loss
from nnunetv2.training.loss.dice import SoftDiceLoss, MemoryEfficientSoftDiceLoss
from typing import Callable

'''
Paper: https://ieeexplore.ieee.org/abstract/document/9611074
Code: https://github.com/YaoleiQi/Examinee-Examiner-Network
'''
class DropCrossEntropyLoss(nn.Module):
    """
    只适用于num_classes=2的情况
    """
    def __init__(self, apply_nonlin: Callable = None, alpha=0.4, smooth=1e-6):
        super().__init__()
        self.alpha = alpha
        self.smooth = smooth
        self.apply_nonlin = apply_nonlin

    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        '''
        参照 RobustCrossEntropyLoss
        '''
        if target.ndim == input.ndim:
            assert target.shape[1] == 1
            target = target[:, 0]

        if self.apply_nonlin is not None:
            input = self.apply_nonlin(input)
        if len(input.shape) == 5:
            input = input[:, 1, :, :, :]
        else:
            input = input[:, 1, :, :]
        # target = target[:, 1, :, :, :]
      
        w = torch.abs(target - input)
        w = torch.round(w + self.alpha)

        loss_ce = -((torch.sum(w * target * torch.log(input + self.smooth)) / torch.sum(w * target+ self.smooth)) +
                             (torch.sum(w * (1 - target) * torch.log(1 - input + self.smooth)) / torch.sum(w * (1 - target) + self.smooth)))/2
        return loss_ce
    


