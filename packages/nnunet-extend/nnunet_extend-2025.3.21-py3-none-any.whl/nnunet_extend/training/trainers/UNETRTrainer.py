from nnunet_extend.network_architecture.monai_model import UNETR
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder, DropCETrainer
from nnunet_extend.training.trainers.base import lr1e4Trainer

@TRAINERS.register_module()
class UNETR3D128Trainer(nnUNetTrainerNoDeepSupervisionNoDecoder, lr1e4Trainer):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:


        return UNETR(
            img_size = 128,
            in_channels = num_input_channels,
            out_channels = num_output_channels,
            feature_size = 16,
            hidden_size = 768,
            mlp_dim = 3072,
            num_heads = 12,
            proj_type= "conv",
            norm_name = "instance",
            conv_block = True,
            res_block = True,
            dropout_rate = 0.0,
            spatial_dims = 3,
            qkv_bias = False,
            save_attn = False,
        )
    
@TRAINERS.register_module()
class UNETR3D128DropCETrainer(UNETR3D128Trainer, DropCETrainer):
    pass
