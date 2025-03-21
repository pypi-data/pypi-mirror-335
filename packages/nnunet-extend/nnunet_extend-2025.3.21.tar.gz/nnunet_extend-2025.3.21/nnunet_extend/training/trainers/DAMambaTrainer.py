from nnunet_extend.network_architecture.mmseg import MMSegModel
from nnunet_extend.training.trainers.base import lr6e5Trainer, lr1e4Trainer
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision
import torch
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from mmengine.config import Config
import nnunet_extend
import os

@TRAINERS.register_module()
class DAMambaUperBaseTrainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        model = MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_base.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )
        # 没有checkpoint时, 训练loss会变成nan
        imagenet_checkpoint = os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'checkpoint', 'DAMamba-B.pth')
        if os.path.exists(imagenet_checkpoint):
            checkpoint = torch.load(imagenet_checkpoint, weights_only=False, map_location='cpu')
            model.model.backbone.load_state_dict(checkpoint['model'], strict=False)
            print('Load imagenet checkpoint')

        return model

@TRAINERS.register_module()
class DAMambaUperSmallTrainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        model = MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_small.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )
        # 没有checkpoint时, 训练loss会变成nan
        imagenet_checkpoint = os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'checkpoint', 'DAMamba-S.pth')
        if os.path.exists(imagenet_checkpoint):
            checkpoint = torch.load(imagenet_checkpoint, weights_only=False, map_location='cpu')
            model.model.backbone.load_state_dict(checkpoint['model'], strict=False)
            print('Load imagenet checkpoint')

        return model


@TRAINERS.register_module()
class DAMambaUperTinyTrainer(nnUNetTrainerCustomDeepSupervision, lr6e5Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        model = MMSegModel(
            input_channels=num_input_channels,
            num_classes=num_output_channels,
            cfg=Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_tiny.py')),
            final_up=4,
            deep_supervision=enable_deep_supervision
        )
        # 没有checkpoint时, 训练loss会变成nan
        imagenet_checkpoint = os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'checkpoint', 'DAMamba-T.pth')
        if os.path.exists(imagenet_checkpoint):
            checkpoint = torch.load(imagenet_checkpoint, weights_only=False, map_location='cpu')
            model.model.backbone.load_state_dict(checkpoint['model'], strict=False)
            print('Load imagenet checkpoint')
        return model
