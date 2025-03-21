import sys

from .DSCNet.DSCNet_2D.S3_DSCNet_pro import DSCNet_pro as DSCNet_pro_2D
from .DSCNet.DSCNet_2D.S3_DSCNet import DSCNet as DSCNet_2D
from .DSCNet.DSCNet_3D.S3_DSCNet import DSCNet as DSCNet_3D
from .DSCNet.DSCNet_3DTiny import DSCNet_3DTiny

from .monai_model import SegResNet, UNet, UNETR, SwinUNETR, VNet, AttentionUnet

from .torchvision_model_zoo import lraspp_mobilenet_v3_large, deeplabv3_resnet50, deeplabv3_resnet101, deeplabv3_mobilenet_v3_large, fcn_resnet50, fcn_resnet101


try:
    from .BiFormer.backbones.biformer import BiFormer
    from .DeBiFormer.backbones.debiformer import debi_tiny, debi_small, debi_base
    from .Samba.backbones.samba import Samba
except:
    print("mmseg not installed. models are not available.")
    
try:
    from .DAMamba.backbones.DAMamba import DAMamba_tiny, DAMamba_small, DAMamba_base
except ImportError:
    print("DAMamba not installed. models are not available.")