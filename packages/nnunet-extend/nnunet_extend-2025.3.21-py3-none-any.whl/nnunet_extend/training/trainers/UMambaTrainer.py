from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunet_extend.training.trainers.base import lr1e4Trainer, lr6e5Trainer
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans

@TRAINERS.register_module()
class UMambaBot3DTainer(lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return get_network_from_plans(
            'nnunet_extend.network_architecture.UMamba.UMambaBot_3d.UMambaBot',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
    )
            
@TRAINERS.register_module()
class UMambaBot2DTainer(lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return get_network_from_plans(
            'nnunet_extend.network_architecture.UMamba.UMambaBot_2d.UMambaBot',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
        )

@TRAINERS.register_module()
class UMambaEnc2D128Tainer(lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:
        arch_init_kwargs['input_size'] = (128, 128)
        return get_network_from_plans(
            'nnunet_extend.network_architecture.UMamba.UMambaEnc_2d.UMambaEnc',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
        )
    

@TRAINERS.register_module()
class UMambaEnc3D128Tainer(nnUNetTrainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:
        arch_init_kwargs['input_size'] = (128, 128, 128)
        return get_network_from_plans(
            'nnunet_extend.network_architecture.UMamba.UMambaEnc_3d.UMambaEnc',
            arch_init_kwargs,
            arch_init_kwargs_req_import,
            num_input_channels,
            num_output_channels,
            enable_deep_supervision
        )