from nnunet_extend.network_architecture.mmseg import MMSegModel
from nnunet_extend.training.trainers.base import lr6e5Trainer
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision
import torch
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from mmengine.config import Config
import nnunet_extend
import os

@TRAINERS.register_module()
class DeBiFormerFPNSmall512Trainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'fpn_512_debi_small.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )


@TRAINERS.register_module()
class DeBiFormerFPNBase512Trainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'fpn_512_debi_base.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )
    
@TRAINERS.register_module()
class DeBiFormerUperSmall512Trainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'upernet_512_debi_small.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )
    
@TRAINERS.register_module()
class DeBiFormerUperBase512Trainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'upernet_512_debi_base.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )