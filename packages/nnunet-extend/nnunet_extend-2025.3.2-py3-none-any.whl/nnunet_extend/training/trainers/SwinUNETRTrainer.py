from nnunet_extend.network_architecture.monai_model import SwinUNETR
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder
from nnunet_extend.training.trainers.base import lr1e4Trainer

@TRAINERS.register_module()
class SwinUNETR3D128Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder, lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return SwinUNETR(
            img_size = 128,
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            depths = (2, 2, 2, 2),
            num_heads = (3, 6, 12, 24),
            feature_size = 24,
            norm_name = "instance",
            drop_rate = 0.0,
            attn_drop_rate = 0.0,
            dropout_path_rate = 0.0,
            normalize = True,
            use_checkpoint = False,
            spatial_dims = 3,
            downsample = "merging",
            use_v2 = False
        )
    