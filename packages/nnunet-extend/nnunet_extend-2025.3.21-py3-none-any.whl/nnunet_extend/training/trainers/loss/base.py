from nnunetv2.training.nnUNetTrainer.variants.loss.nnUNetTrainerCELoss import nnUNetTrainerCELoss, nnUNetTrainerCELoss_5epochs
from nnunetv2.training.nnUNetTrainer.variants.loss.nnUNetTrainerDiceLoss import nnUNetTrainerDiceLoss, nnUNetTrainerDiceCELoss_noSmooth
from nnunetv2.training.nnUNetTrainer.variants.loss.nnUNetTrainerTopkLoss import nnUNetTrainerTopk10Loss, nnUNetTrainerTopk10LossLS01, nnUNetTrainerDiceTopK10Loss
from nnunetv2.training.nnUNetTrainer.variants.network_architecture.nnUNetTrainerNoDeepSupervision import nnUNetTrainerNoDeepSupervision
from nnunet_extend.registry.registry import TRAINERS
from nnunet_extend.training.loss import DeepSupervisionLoss
from nnunet_extend.training.trainers.base import nnUNetTrainerNoDecoder

TRAINERS.register_module(name='nnUNetTrainerCELoss', module=nnUNetTrainerCELoss)
TRAINERS.register_module(name='nnUNetTrainerCELoss_5epochs', module=nnUNetTrainerCELoss_5epochs)
TRAINERS.register_module(name='nnUNetTrainerDiceLoss', module=nnUNetTrainerDiceLoss)
TRAINERS.register_module(name='nnUNetTrainerDiceCELoss_noSmooth', module=nnUNetTrainerDiceCELoss_noSmooth)
TRAINERS.register_module(name='nnUNetTrainerTopk10Loss', module=nnUNetTrainerTopk10Loss)
TRAINERS.register_module(name='nnUNetTrainerTopk10LossLS01', module=nnUNetTrainerTopk10LossLS01)
TRAINERS.register_module(name='nnUNetTrainerDiceTopK10Loss', module=nnUNetTrainerDiceTopK10Loss)



class nnUNetTrainerNoDeepSupervisionNoDecoder(nnUNetTrainerNoDeepSupervision, nnUNetTrainerNoDecoder):
    pass

class nnUNetTrainerCustomDeepSupervision(nnUNetTrainerNoDecoder):
    def _build_loss(self):
        return DeepSupervisionLoss(super()._build_loss().loss, weight_mode='exp')