from nnunet_extend.network_architecture.mmseg import MMSegModel
from nnunet_extend.training.trainers.base import lr6e5Trainer
from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder, nnUNetTrainerCustomDeepSupervision
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from mmengine.config import Config
import nnunet_extend
import os


@TRAINERS.register_module()
class CCNet_Res50_d8Trainer(nnUNetTrainerCustomDeepSupervision):
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
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'CCNet', 'configs', 'ccnet_r50-d8.py')),
            final_up=8,
            deep_supervision=enable_deep_supervision
        )

@TRAINERS.register_module()
class CCNet_Res101_d8Trainer(nnUNetTrainerCustomDeepSupervision):
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
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'CCNet', 'configs', 'ccnet_r50-d8.py')),
            final_up=8,
            deep_supervision=enable_deep_supervision
        )