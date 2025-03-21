from nnunet_extend.network_architecture.MedNeXt.create_mednext_v1 import create_mednext_v1
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision
from nnunet_extend.training.trainers.base import lr6e5Trainer

@TRAINERS.register_module()
class MedNeXtSmallTrainer(nnUNetTrainerCustomDeepSupervision):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return create_mednext_v1(
            num_input_channels=num_input_channels,
            num_classes=num_output_channels,
            model_id='S',
            kernel_size=3,
            deep_supervision=enable_deep_supervision
        )
    
@TRAINERS.register_module()
class MedNeXtBaseTrainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return create_mednext_v1(
            num_input_channels=num_input_channels,
            num_classes=num_output_channels,
            model_id='B',
            kernel_size=3,
            deep_supervision=enable_deep_supervision
        )

@TRAINERS.register_module()
class MedNeXtMediumTrainer(nnUNetTrainerCustomDeepSupervision):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return create_mednext_v1(
            num_input_channels=num_input_channels,
            num_classes=num_output_channels,
            model_id='M',
            kernel_size=3,
            deep_supervision=enable_deep_supervision
        )

@TRAINERS.register_module()
class MedNeXtLargeTrainer(nnUNetTrainerCustomDeepSupervision):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return create_mednext_v1(
            num_input_channels=num_input_channels,
            num_classes=num_output_channels,
            model_id='L',
            kernel_size=3,
            deep_supervision=enable_deep_supervision
        )