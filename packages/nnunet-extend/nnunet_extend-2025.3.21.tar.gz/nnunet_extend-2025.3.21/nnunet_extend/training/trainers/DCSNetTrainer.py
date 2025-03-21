from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder, nnUNetTrainerSkeletonRecall
from nnunet_extend.training.trainers.loss.DropCETrainer import DropCETrainer
from nnunet_extend.network_architecture import DSCNet_2D, DSCNet_3D, DSCNet_pro_2D, DSCNet_3DTiny
import torch
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS



@TRAINERS.register_module()
class DSCNet2DTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return DSCNet_2D(
            n_channels=num_input_channels,
            n_classes=num_output_channels,
            kernel_size=9,
            extend_scope=1,
            if_offset=True,
            device=torch.device('cuda'),
            number=16
        )
    
@TRAINERS.register_module()
class DSCNet2DDropCETrainer(DSCNet2DTrainer, DropCETrainer):
    pass

@TRAINERS.register_module()
class DSCNet2DProTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return DSCNet_pro_2D(
            n_channels=num_input_channels,
            n_classes=num_output_channels,
            kernel_size=9,
            extend_scope=1,
            if_offset=True,
            device=torch.device('cuda'),
            number=16
        )
    
@TRAINERS.register_module()
class DSCNet2DProDropCETrainer(DSCNet2DProTrainer, DropCETrainer):
    pass



@TRAINERS.register_module()
class DSCNet3DTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return DSCNet_3D(
            n_channels=num_input_channels,
            n_classes=num_output_channels,
            kernel_size=3,
            extend_scope=1,
            if_offset=True,
            device=torch.device('cuda'),
            number=16
        )
    

@TRAINERS.register_module()
class DSCNet3DDropCETrainer(DSCNet3DTrainer, DropCETrainer):
    pass

@TRAINERS.register_module()
class DSCNet3DTinyTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return DSCNet_3DTiny(
            n_channels=num_input_channels,
            n_classes=num_output_channels,
            kernel_size=3,
            extend_scope=1,
            if_offset=True,
            device=torch.device('cuda'),
            number=16
        )
    

@TRAINERS.register_module()
class DSCNet3DTinyDropCETrainer(DSCNet3DTinyTrainer, DropCETrainer):
    pass

@TRAINERS.register_module()
class DSCNet3DTinySkeletonRecallTrainer(DSCNet3DTinyTrainer, nnUNetTrainerSkeletonRecall):
    pass