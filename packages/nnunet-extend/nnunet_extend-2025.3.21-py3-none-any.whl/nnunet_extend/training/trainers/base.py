from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunetv2.training.nnUNetTrainer.variants.network_architecture.nnUNetTrainerNoDeepSupervision import nnUNetTrainerNoDeepSupervision
from nnunetv2.training.nnUNetTrainer.variants.benchmarking.nnUNetTrainerBenchmark_5epochs import nnUNetTrainerBenchmark_5epochs
from nnunet_extend.registry import TRAINERS
from torch._dynamo import OptimizedModule
import torch


TRAINERS.register_module(name='nnUNetTrainer', module=nnUNetTrainer)
TRAINERS.register_module(name='nnUNetTrainerNoDeepSupervision', module=nnUNetTrainerNoDeepSupervision)
TRAINERS.register_module(name='nnUNetTrainerBenchmark_5epochs', module=nnUNetTrainerBenchmark_5epochs)

class nnUNetTrainerNoDecoder(nnUNetTrainer):
    def set_deep_supervision_enabled(self, enabled):
        if self.is_ddp:
            mod = self.network.module
        else:
            mod = self.network
        if isinstance(mod, OptimizedModule):
            mod = mod._orig_mod

        # some models do not have decoder
        # mod.decoder.deep_supervision = enabled

class lr6e5Trainer(nnUNetTrainer):
    def __init__(
        self,
        plans: dict,
        configuration: str,
        fold: int,
        dataset_json: dict,
        device: torch.device = torch.device("cuda"),
    ):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.initial_lr = 6e-5

class lr1e4Trainer(nnUNetTrainer):
    def __init__(
        self,
        plans: dict,
        configuration: str,
        fold: int,
        dataset_json: dict,
        device: torch.device = torch.device("cuda"),
    ):
        super().__init__(plans, configuration, fold, dataset_json, device)
        self.initial_lr = 1e-4