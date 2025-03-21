from monai.losses import (
    Dice, DiceCELoss, DiceFocalLoss, DiceLoss, MaskedDiceLoss,
    GeneralizedDiceFocalLoss, GeneralizedDiceLoss, GeneralizedWassersteinDiceLoss,
    FocalLoss,
    HausdorffDTLoss, LogHausdorffDTLoss,
    TverskyLoss,
)

from mmseg.models.losses import (
    BoundaryLoss, LovaszLoss, OhemCrossEntropy, SiLogLoss
)