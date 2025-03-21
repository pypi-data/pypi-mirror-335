from nnunet_extend.network_architecture.CoTr.ResTranUnet import ResTranUnet
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision

@TRAINERS.register_module()
class CoTr64Trainer(nnUNetTrainerCustomDeepSupervision):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return ResTranUnet(
            in_channels=num_input_channels,
            num_classes=num_output_channels,
            norm_cfg='IN', 
            activation_cfg='ReLU', 
            img_size=(64, 64, 64),
            weight_std=False, 
            deep_supervision=enable_deep_supervision
        )
    
@TRAINERS.register_module()
class CoTr128Trainer(nnUNetTrainerCustomDeepSupervision):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return ResTranUnet(
            in_channels=num_input_channels,
            num_classes=num_output_channels,
            norm_cfg='IN', 
            activation_cfg='ReLU', 
            img_size=(128, 128, 128),
            weight_std=False, 
            deep_supervision=enable_deep_supervision
        )
        