from nnunet_extend.network_architecture.mmseg import MMSegModel
from mmengine.config import Config
import nnunet_extend
import os
import torch

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'upernet_512_debi_base.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'upernet_512_debi_small.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'fpn_512_debi_base.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DeBiFormer', 'configs', 'fpn_512_debi_small.py'))
    model = MMSegModel(3, 1, cfg, 4, False).to(device)
    x = torch.randn(4, 3, 512, 512).to(device)
    print(model(x).shape)

