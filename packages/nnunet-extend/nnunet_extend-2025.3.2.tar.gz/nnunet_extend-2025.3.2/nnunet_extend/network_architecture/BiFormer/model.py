from nnunet_extend.network_architecture.mmseg import MMSegModel
from mmengine.config import Config
import nnunet_extend
import os
import torch

if __name__ == '__main__':
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'BiFormer', 'configs', 'upernet_biformer_base_512.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'BiFormer', 'configs', 'upernet_biformer_small_512.py'))
    model = MMSegModel(1, 2, cfg, final_up=4).to(device)
    # model = BiFormerSmall512(1, 2).to(device)
    x = torch.randn(2, 1, 1280, 512).to(device)
    x = model(x)
    for i in x:
        print(i.shape)

