_base_ = [
    './upernet_DAMamba.py',
]
# optimizer
model = dict(
    backbone=dict(
        pretrained=None,
        # pretrained='path/DAMamba-T.pth',
        type='DAMamba_tiny',
    ),
    decode_head=dict(
        in_channels=[80, 160, 320, 512],
        num_classes=150
    ),
    auxiliary_head=dict(
        in_channels=320,
        num_classes=150
    ))
