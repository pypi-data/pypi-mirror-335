from nnunet_extend.network_architecture.TransUNet.vit_seg_modeling import VisionTransformer as ViT_seg
from nnunet_extend.network_architecture.TransUNet.vit_seg_modeling import CONFIGS as CONFIGS_ViT_seg
import numpy as np
# 'ViT-B_16'
# 'ViT-B_32'
# 'ViT-L_16'
# 'ViT-L_32'
# 'ViT-H_14'
# 'R50-ViT-B_16'
# 'R50-ViT-L_16'

def transunet(vit_name='R50-ViT-B_16', num_classes=9, n_skip=3, img_size=224, vit_patches_size=16, pretrained_path=None):
    config_vit = CONFIGS_ViT_seg[vit_name]
    config_vit.n_classes = num_classes
    config_vit.n_skip = n_skip

    if vit_name.find('R50') != -1:
        config_vit.patches.grid = (int(img_size / vit_patches_size), int(img_size / vit_patches_size))

    net = ViT_seg(config_vit, img_size=img_size, num_classes=num_classes)
    if pretrained_path is not None:
        net.load_from(weights=np.load(pretrained_path))
    return net

if __name__=='__main__':
    import torch
    vit_name = ['ViT-B_16', 'ViT-B_32', 'ViT-L_16', 'ViT-L_32', 'R50-ViT-B_16', 'R50-ViT-L_16']
    n_kip = [0, 0 , 0, 0, 0, 3, 3]
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    inputs = torch.randn(2, 3, 640, 640).to(device)
    net = transunet('ViT-B_16', n_skip=0, img_size=640, vit_patches_size=16).to(device)
    outputs = net(inputs)
    print(outputs.shape)
    # for name, skip in zip(vit_name, n_kip):
    #     print(name)
    #     net = transunet(name, n_skip=skip, img_size=512).to(device)
    #     outputs = net(inputs)
    #     print(outputs.shape)