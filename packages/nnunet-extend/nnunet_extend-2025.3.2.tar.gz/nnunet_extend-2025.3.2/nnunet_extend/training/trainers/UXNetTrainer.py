from nnunet_extend.network_architecture.UXNet3D.network_backbone import UXNET
from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from torch import nn
from typing import List, Tuple, Union
from nnunet_extend.registry.registry import TRAINERS
from torch._dynamo import OptimizedModule
from nnunet_extend.training.trainers.loss import nnUNetTrainerNoDeepSupervisionNoDecoder
from monai.losses import DeepSupervisionLoss
from nnunet_extend.training.trainers.loss import nnUNetTrainerCustomDeepSupervision


@TRAINERS.register_module()
class UXNET3DTrainer(nnUNetTrainerNoDeepSupervisionNoDecoder):
    @staticmethod
    def build_network_architecture(architecture_class_name: str,
                                   arch_init_kwargs: dict,
                                   arch_init_kwargs_req_import: Union[List[str], Tuple[str, ...]],
                                   num_input_channels: int,
                                   num_output_channels: int,
                                   enable_deep_supervision: bool = True) -> nn.Module:

        return UXNET(
            in_chans=num_input_channels,
            out_chans=num_output_channels,
            depths=[2, 2, 2, 2],
            feat_size=[48, 96, 192, 384],
            drop_path_rate=0,
            layer_scale_init_value=1e-6,
            spatial_dims=3,
        )
    
