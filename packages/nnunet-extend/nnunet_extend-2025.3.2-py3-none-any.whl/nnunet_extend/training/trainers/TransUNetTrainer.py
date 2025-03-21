from nnunet_extend.network_architecture.TransUNet import transunet
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from torch._dynamo import OptimizedModule
from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder
from monai.losses import DeepSupervisionLoss
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision


@TRAINERS.register_module()
class TransUNetViT_B_16_224Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return transunet(vit_name='ViT-B_16', num_classes=num_output_channels, n_skip=0, img_size=640, vit_patches_size=16, pretrained_path=None)
    
@TRAINERS.register_module()
class TransUNetViT_L_16_224Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return transunet(vit_name='ViT-L_16', num_classes=num_output_channels, n_skip=0, img_size=224, vit_patches_size=16, pretrained_path=None) 

@TRAINERS.register_module()
class TransUNetR50Vit_B_16_224Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return transunet(vit_name='R50-ViT-B_16', num_classes=num_output_channels, n_skip=0, img_size=224, vit_patches_size=16, pretrained_path=None)
    
@TRAINERS.register_module()
class TransUNetR50Vit_L_16_224Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return transunet(vit_name='R50-ViT-L_16', num_classes=num_output_channels, n_skip=0, img_size=224, vit_patches_size=16, pretrained_path=None)