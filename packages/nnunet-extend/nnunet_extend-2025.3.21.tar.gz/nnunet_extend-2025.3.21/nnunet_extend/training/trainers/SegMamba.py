from nnunet_extend.network_architecture.SegMamba import SegMamba
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


        return SegMamba(
            in_chans=num_input_channels,
            out_chans=num_output_channels,
            depths=[2, 2, 2, 2],
            feat_size=[48, 96, 192, 384],
            drop_path_rate=0,
            layer_scale_init_value=1e-6,
            hidden_size = 768,
            norm_name = "instance",
            conv_block = True,
            res_block = True,
            spatial_dims=3,
        )
    