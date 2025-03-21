import sys
from .base import nnUNetTrainer, nnUNetTrainerNoDeepSupervision
from .DCSNetTrainer import DSCNet2DTrainer
from .loss import *
from .CoTrTrainer import CoTr64Trainer, CoTr128Trainer
from .MedNeXtTrainer import MedNeXtSmallTrainer
from .TransUNetTrainer import TransUNetViT_B_16_224Trainer, TransUNetViT_L_16_224Trainer, TransUNetR50Vit_B_16_224Trainer, TransUNetR50Vit_L_16_224Trainer
from .UXNetTrainer import UXNET3DTrainer
from .UNETRTrainer import UNETR3D128Trainer
from .SwinUNETRTrainer import SwinUNETR3D128Trainer
from .DFormerTrainer import DFormerTrainer

# if sys.platform.startswith("linux"):
try:
    from .BiFormerTrainer import BiFormerUperBase512Trainer, BiFormerUperSmall512Trainer, BiFormerUperBase512TrainerNoDeepSupervision, BiFormerUperSmall512TrainerNoDeepSupervision
    from .DeBiFormerTrainer import DeBiFormerFPNBase512Trainer, DeBiFormerFPNSmall512Trainer, DeBiFormerUperSmall512Trainer, DeBiFormerUperBase512Trainer
    from .CCNetTrainer import CCNet_Res50_d8Trainer, CCNet_Res101_d8Trainer
    from .DAMambaTrainer import DAMambaUperBaseTrainer, DAMambaUperSmallTrainer, DAMambaUperTinyTrainer
except ImportError:
    print("mmseg not installed. models are not available.")

try:
    from .UMambaTrainer import UMambaBot3DTainer, UMambaBot2DTainer, UMambaEnc2D128Tainer, UMambaEnc3D128Tainer
    from .LKMUNetTrainer import LKMUNetTrainer
    from .LightMUNetTrainer import LightMUNet3DTrainer, LightMUNet2DTrainer
except ImportError:
    print("mamba_ssm not installed. models are not available.")
