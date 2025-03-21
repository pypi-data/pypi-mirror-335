from mmengine.config import Config
from nnunet_extend.network_architecture.mmseg import MMSegModel
import nnunet_extend
import os
import torch

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'CCNet', 'configs', 'ccnet_r50-d8.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'CCNet', 'configs', 'ccnet_r101-d8.py'))
    model = MMSegModel(3, 1, cfg, 0, False).to(device)
    x = torch.randn(4, 3, 512, 512).to(device)
    print(model(x).shape)

