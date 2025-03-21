_base_ = [
    './upernet_DAMamba.py',
]
# optimizer
model = dict(
    backbone=dict(
        pretrained=None,
        # pretrained='path/DAMamba-B.pth',
        type='DAMamba_base',
    ),
    decode_head=dict(
        in_channels=[112, 224, 448, 640],
        num_classes=150
    ),
    auxiliary_head=dict(
        in_channels=448,
        num_classes=150
    ))

