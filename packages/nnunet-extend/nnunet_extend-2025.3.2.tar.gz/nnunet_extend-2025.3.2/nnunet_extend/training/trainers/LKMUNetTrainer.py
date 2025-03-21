from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunet_extend.training.trainers.base import lr1e4Trainer, lr6e5Trainer
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans

@TRAINERS.register_module()
class LKMUNetTrainer(lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return get_network_from_plans(
            'nnunet_extend.network_architecture.LKMUNet.LKMUNet',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
    )
