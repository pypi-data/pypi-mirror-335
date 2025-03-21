import torch
from nnunetv2.training.loss.dice import SoftDiceLoss, MemoryEfficientSoftDiceLoss
from nnunetv2.training.loss.robust_ce_loss import RobustCrossEntropyLoss
from nnunetv2.training.loss.compound_losses import DC_and_CE_loss
from nnunetv2.utilities.helpers import softmax_helper_dim1
from torch import nn
from nnunet_extend.training.loss.SkeletonRecallLoss import SoftSkeletonRecallLoss
from nnunet_extend.training.loss.DropCELoss import DropCrossEntropyLoss
from nnunet_extend.training.loss.cbDiceLoss import SoftcbDiceLoss, SoftclMDiceLoss
from nnunet_extend.training.loss.clDiceLoss import SoftclDiceLoss
from nnunet_extend.training.loss.BoundaryDoULoss import BoundaryDoULoss

# from https://github.com/MIC-DKFZ/Skeleton-Recall.git
class DC_SkelREC_and_CE_loss(nn.Module):
    def __init__(self, soft_dice_kwargs, soft_skelrec_kwargs, ce_kwargs, weight_ce=1, weight_dice=1, weight_srec=1, 
                 ignore_label=None, dice_class=MemoryEfficientSoftDiceLoss):
        """
        Weights for CE and Dice do not need to sum to one. You can set whatever you want.
        :param soft_dice_kwargs:
        :param soft_skelrec_kwargs:
        :param ce_kwargs:
        :param aggregate:
        :param square_dice:
        :param weight_ce:
        :param weight_dice:
        """
        super(DC_SkelREC_and_CE_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_dice = weight_dice
        self.weight_ce = weight_ce
        self.weight_srec = weight_srec
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.dc = dice_class(apply_nonlin=softmax_helper_dim1, **soft_dice_kwargs)
        self.srec = SoftSkeletonRecallLoss(apply_nonlin=softmax_helper_dim1, **soft_skelrec_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor, skel: torch.Tensor, loss_mask: torch.Tensor=None):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """

        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(DC_and_CE_loss)'
            mask = target != self.ignore_label
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_dice = torch.where(mask, target, 0)
            target_skel = torch.where(mask, skel, 0)
            num_fg = mask.sum()
        else:
            target_dice = target
            target_skel = skel
            mask = loss_mask

        dc_loss = self.dc(net_output, target_dice, loss_mask=mask) \
            if self.weight_dice != 0 else 0
        srec_loss = self.srec(net_output, target_skel, loss_mask=mask) \
            if self.weight_srec != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0]) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0

        result = self.weight_ce * ce_loss + self.weight_dice * dc_loss + self.weight_srec * srec_loss
        return result
    

class DC_and_DropCE_loss(DC_and_CE_loss):
    def __init__(self, soft_dice_kwargs, ce_kwargs, weight_ce=1, weight_dice=1, ignore_label=None,
                 dice_class=SoftDiceLoss):
        super(DC_and_DropCE_loss, self).__init__(soft_dice_kwargs, {}, weight_ce, weight_dice, ignore_label, dice_class)
        self.ce = DropCrossEntropyLoss(**ce_kwargs)


class DC_and_CE_and_CBDC_loss(nn.Module):
    def __init__(self, soft_dice_kwargs, ce_kwargs, cbdc_kwargs, weight_ce=1, weight_dice=1, weight_cbdice=1, ignore_label=None,
                 dice_class=SoftDiceLoss):
        """
        Weights for CE and Dice do not need to sum to one. You can set whatever you want.
        :param soft_dice_kwargs:
        :param ce_kwargs:
        :param ti_kwargs:
        :param weight_ce:
        :param weight_dice:
        :param weight_ti:
        """
        super(DC_and_CE_and_CBDC_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_dice = weight_dice
        self.weight_ce = weight_ce
        self.weight_cbdice = weight_cbdice
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.dc = dice_class(apply_nonlin=softmax_helper_dim1, **soft_dice_kwargs)
        self.cbdice = SoftcbDiceLoss(**cbdc_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor, t_skeletonize_flage=False):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """
        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(DC_and_CE_loss)'
            mask = (target != self.ignore_label).bool()
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_dice = torch.clone(target)
            target_dice[target == self.ignore_label] = 0
            num_fg = mask.sum()
        else:
            target_dice = target
            mask = None

        dc_loss = self.dc(net_output, target_dice, loss_mask=mask) \
            if self.weight_dice != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0].long()) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0

        cbdice_loss = self.cbdice(net_output, target, t_skeletonize_flage=t_skeletonize_flage) if self.weight_cbdice != 0 else 0

        result = self.weight_ce * ce_loss + self.weight_dice * dc_loss + self.weight_cbdice * cbdice_loss
        return result

class DC_and_CE_and_CL_M_DC_loss(nn.Module):
    def __init__(self, soft_dice_kwargs, ce_kwargs, cbdc_kwargs, weight_ce=1, weight_dice=1, weight_clMdice=1, ignore_label=None,
                 dice_class=SoftDiceLoss):
        """
        Weights for CE and Dice do not need to sum to one. You can set whatever you want.
        :param soft_dice_kwargs:
        :param ce_kwargs:
        :param ti_kwargs:
        :param weight_ce:
        :param weight_dice:
        :param weight_ti:
        """
        super(DC_and_CE_and_CL_M_DC_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_dice = weight_dice
        self.weight_ce = weight_ce
        self.weight_clMdice = weight_clMdice
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.dc = dice_class(apply_nonlin=softmax_helper_dim1, **soft_dice_kwargs)
        self.clMdice = SoftclMDiceLoss(**cbdc_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor, t_skeletonize_flage=False):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """
        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(DC_and_CE_loss)'
            mask = (target != self.ignore_label).bool()
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_dice = torch.clone(target)
            target_dice[target == self.ignore_label] = 0
            num_fg = mask.sum()
        else:
            target_dice = target
            mask = None

        dc_loss = self.dc(net_output, target_dice, loss_mask=mask) \
            if self.weight_dice != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0].long()) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0

        clMdice_loss = self.clMdice(net_output, target, t_skeletonize_flage=t_skeletonize_flage) if self.weight_clMdice != 0 else 0

        result = self.weight_ce * ce_loss + self.weight_dice * dc_loss + self.weight_clMdice * clMdice_loss
        return result


class DC_and_CE_and_CLDC_loss(nn.Module):
    def __init__(self, soft_dice_kwargs, ce_kwargs, cldc_kwargs, weight_ce=1, weight_dice=1, weight_cldice=1, ignore_label=None,
                 dice_class=SoftDiceLoss):
        """
        Weights for CE and Dice do not need to sum to one. You can set whatever you want.
        :param soft_dice_kwargs:
        :param ce_kwargs:
        :param ti_kwargs:
        :param weight_ce:
        :param weight_dice:
        :param weight_ti:
        """
        super(DC_and_CE_and_CLDC_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_dice = weight_dice
        self.weight_ce = weight_ce
        self.weight_cldice = weight_cldice
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.dc = dice_class(apply_nonlin=softmax_helper_dim1, **soft_dice_kwargs)
        self.cldice = SoftclDiceLoss(**cldc_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor, t_skeletonize_flage=False):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """
        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(DC_and_CE_loss)'
            mask = (target != self.ignore_label).bool()
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_dice = torch.clone(target)
            target_dice[target == self.ignore_label] = 0
            num_fg = mask.sum()
        else:
            target_dice = target
            mask = None

        dc_loss = self.dc(net_output, target_dice, loss_mask=mask) \
            if self.weight_dice != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0].long()) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0

        cldice_loss = self.cldice(net_output, target, t_skeletonize_flage=t_skeletonize_flage) if self.weight_cldice != 0 else 0

        result = self.weight_ce * ce_loss + self.weight_dice * dc_loss + self.weight_cldice * cldice_loss
        return result


class B_DoU_and_CE_loss(nn.Module):
    def __init__(self, ce_kwargs, bdou_kwargs, weight_ce=1, weight_bdou=1, ignore_label=None):
        """
        :param ce_kwargs:
        :param bdou_kwargs:
        :param aggregate:
        :param weight_ce:
        :param weight_bdou:
        """
        super(B_DoU_and_CE_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_bdou = weight_bdou
        self.weight_ce = weight_ce
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.bdou = BoundaryDoULoss(**bdou_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """
        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(B_DoU_and_CE_loss)'
            mask = (target != self.ignore_label).bool()
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_bdou = torch.clone(target)
            target_bdou[target == self.ignore_label] = 0
            num_fg = mask.sum()
        else:
            target_bdou = target
            mask = None

        bdou_loss = self.bdou(net_output, target) \
            if self.weight_bdou != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0].long()) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0

        result = self.weight_ce * ce_loss + self.weight_bdou * bdou_loss
        return result


class DC_CE_and_B_DoU_loss(nn.Module):
    def __init__(self, soft_dice_kwargs, ce_kwargs, bdou_kwargs, weight_ce=1, weight_dice=1, weight_bdou=1, ignore_label=None,
                 dice_class=SoftDiceLoss):
        """
        Weights for CE and Dice do not need to sum to one. You can set whatever you want.
        :param soft_dice_kwargs:
        :param ce_kwargs:
        :param bdou_kwargs:
        :param aggregate:
        :param square_dice:
        :param weight_ce:
        :param weight_dice:
        :param weight_bdou:
        """
        super(DC_CE_and_B_DoU_loss, self).__init__()
        if ignore_label is not None:
            ce_kwargs['ignore_index'] = ignore_label

        self.weight_dice = weight_dice
        self.weight_ce = weight_ce
        self.weight_bdou = weight_bdou
        self.ignore_label = ignore_label

        self.ce = RobustCrossEntropyLoss(**ce_kwargs)
        self.dc = dice_class(apply_nonlin=softmax_helper_dim1, **soft_dice_kwargs)
        self.bdou = BoundaryDoULoss(**bdou_kwargs)

    def forward(self, net_output: torch.Tensor, target: torch.Tensor):
        """
        target must be b, c, x, y(, z) with c=1
        :param net_output:
        :param target:
        :return:
        """
        if self.ignore_label is not None:
            assert target.shape[1] == 1, 'ignore label is not implemented for one hot encoded target variables ' \
                                         '(DC_and_CE_loss)'
            mask = (target != self.ignore_label).bool()
            # remove ignore label from target, replace with one of the known labels. It doesn't matter because we
            # ignore gradients in those areas anyway
            target_dice = torch.clone(target)
            target_dice[target == self.ignore_label] = 0
            num_fg = mask.sum()
        else:
            target_dice = target
            mask = None

        dc_loss = self.dc(net_output, target_dice, loss_mask=mask) \
            if self.weight_dice != 0 else 0
        ce_loss = self.ce(net_output, target[:, 0].long()) \
            if self.weight_ce != 0 and (self.ignore_label is None or num_fg > 0) else 0
        bdou_loss = self.bdou(net_output, target_dice) \
            if self.weight_bdou != 0 else 0

        result = self.weight_ce * ce_loss + self.weight_dice * dc_loss + self.weight_bdou * bdou_loss
        return result
    

if __name__ == '__main__':
    from nnunetv2.utilities.helpers import softmax_helper_dim1
    pred = torch.rand((2, 3, 32, 32, 32))
    ref = torch.randint(0, 3, (2, 1, 32, 32, 32))

    loss = DC_and_DropCE_loss({'batch_dice': False, 'smooth': 1e-5, 'do_bg': False, 'ddp': False},
                                {'apply_nonlin':None, 'alpha': 0.4, 'smooth': 1e-6},
                                weight_ce=1, weight_dice=1, ignore_label=None, dice_class=MemoryEfficientSoftDiceLoss)
    
    # loss = DC_and_DropCE_loss({'batch_dice': False, 'smooth': 1e-5, 'do_bg': False, 'ddp': False},
    #                             {'apply_nonlin':softmax_helper_dim1, 'alpha': 0.4, 'smooth': 1e-6},
    #                             weight_ce=1, weight_dice=1, ignore_label=None, dice_class=MemoryEfficientSoftDiceLoss)
    
    loss1 = DC_and_CE_loss({'batch_dice': False, 'smooth': 1e-5, 'do_bg': False, 'ddp': False},
                                {},
                                weight_ce=1, weight_dice=1, ignore_label=None, dice_class=MemoryEfficientSoftDiceLoss)
    print('loss', loss(pred, ref))
    print('loss1', loss1(pred, ref))
    
    print(loss.ce(pred, ref))
    print(loss.dc(pred, ref))

    print(loss1.ce(pred, ref))
    print(loss1.dc(pred, ref))