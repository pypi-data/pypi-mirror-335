from nnunet_extend.network_architecture.mmseg import MMSegModel
from mmengine.config import Config
import nnunet_extend
import os
import torch

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_base.py'))
    # cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_small.py'))
    cfg = Config.fromfile(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'DAMamba', 'configs', 'upernet_DAMamba_tiny.py'))
    checkpoint = torch.load(os.path.join(nnunet_extend.__path__[0], 'network_architecture', 'checkpoint', 'DAMamba-T.pth'), weights_only=False, map_location='cpu')
    model = MMSegModel(3, 1, cfg, 4, False).to(device)
    model.model.backbone.load_state_dict(checkpoint['model'], strict=False)
    x = torch.randn(4, 3, 512, 512).to(device)
    print(model(x).shape)

