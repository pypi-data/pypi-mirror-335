_base_ = [
    './upernet_DAMamba.py',
]
# optimizer
model = dict(
    backbone=dict(
        pretrained=None,
        # pretrained='path/DAMamba-S.pth',
        type='DAMamba_small',
    ),
    decode_head=dict(
        in_channels=[96, 192, 384, 512],
        num_classes=150
    ),
    auxiliary_head=dict(
        in_channels=384,
        num_classes=150
    ))

