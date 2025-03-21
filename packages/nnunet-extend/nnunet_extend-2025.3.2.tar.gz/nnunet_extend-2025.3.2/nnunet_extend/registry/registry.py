from mmengine.registry import Registry

TRAINERS = Registry('trainer', locations=['nnunet_extend.training.trainers'])
INFERENCES = Registry('inference', locations=['nnunet_extend.inference'])