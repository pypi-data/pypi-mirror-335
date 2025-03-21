from nnunet_extend.network_architecture.DFormer import D_Former3D
from nnunet_extend.training.trainers.base import lr6e5Trainer
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS



@TRAINERS.register_module()
class DFormerTrainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return D_Former3D(
            in_chan=num_input_channels,
            num_classes=num_output_channels,
            embed_dim=96,
            depths=[2, 2, 6, 2],
            num_heads=[3, 6, 12, 24],
            patch_size=(4, 4, 4),
            group_size=(8, 8, 8),
            deep_supervision=enable_deep_supervision,
        )

