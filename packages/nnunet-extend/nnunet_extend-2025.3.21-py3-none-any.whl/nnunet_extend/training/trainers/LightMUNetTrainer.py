from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.network_architecture.LightMUNet import LightMUNet
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans

@TRAINERS.register_module()
class LightMUNet2DTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return LightMUNet(
            spatial_dims=2,
            init_filters = 32,
            in_channels=num_input_channels,
            out_channels=num_output_channels,
            blocks_down=[1, 2, 2, 4],
            blocks_up=[1, 1, 1],
        )

@TRAINERS.register_module()
class LightMUNet3DTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return LightMUNet(
            spatial_dims=3,
            init_filters = 32,
            in_channels=num_input_channels,
            out_channels=num_output_channels,
            blocks_down=[1, 2, 2, 4],
            blocks_up=[1, 1, 1],
        )