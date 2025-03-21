# nnunet_extend
nnunetv2扩展包  
[nnunet使用文档](./documentation/nnUNet.md)  
[nnunet_extend使用文档](./documentation/nnunet_extend.md)

> 推荐环境  
> 
> Ubuntu22.04    
> CUDA 12.4    
> torch 2.6.0    
> nnunetv2 2.6.0  
> mamba-ssm 2.2.4 (pip install mamba-ssm, 编译时间长)  
> mmcv 2.1.0  
> mmsegmentation 1.2.2  
> mmengine 0.10.6  
> causal-conv1d 1.5.0.post8
> 
> Windows下尚未测试合适的环境，部分Trainer无法使用  
> torch2.6.0目前无法安装mmcv和mmseg，对应的部分模型无法使用  
> mamba-ssm和causal-conv1d如未安装，对应的部分模型无法使用  
> 

<div align="center">
  <b>Overview</b>
</div>
<table align="center">
  	<tbody>
		<tr align="center" valign="center">
		<td>
			<b>Supported Models</b>
		</td>
		<td>
			<b>Supported Loss Functions</b>
		</td>
		</tr>
		<tr valign="top">
		<td>
			<ul>
				<li><a href="nnunet_extend/network_architecture/DAMamba/model.py">DAMamba (arXiv'2025)</a> [<a href="
				https://doi.org/10.48550/arXiv.2502.12627">paper</a>] [<a href="https://github.com/ltzovo/DAMamba">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/LightMUNet.py">LightM-UNet (arXiv'2024)</a> [<a href="
				https://doi.org/10.48550/arXiv.2502.12627">paper</a>] [<a href="https://github.com/MrBlankness/LightM-UNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/LKMUNet.py">LKM-UNet (arXiv'2024)</a> [<a href="
				https://doi.org/10.48550/arXiv.2403.07332">paper</a>] [<a href="https://github.com/wjh892521292/LKM-UNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/SegMamba.py">SegMamba (arXiv'2024)</a> [<a href="
				https://doi.org/10.48550/arXiv.2401.13560">paper</a>] [<a href="https://github.com/ge-xing/SegMamba">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/Samba/model.py">Samba (Heliyon'2024)</a> [<a href="
				https://doi.org/10.48550/arXiv.2404.01705">paper</a>] [<a href="https://github.com/zhuqinfeng1999/Samba">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/CoTr/ResTranUnet.py">CoTr (MICCAI'2021)</a> [<a href="https://doi.org/10.1007/978-3-030-87199-4_16">paper</a>] [<a href="https://github.com/YtongXie/CoTr">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/TransUNet/transunet.py">TransUNet (arXiv'2021)</a> [<a href="
				https://doi.org/10.48550/arXiv.2102.04306">paper</a>] [<a href="https://github.com/Beckschen/TransUNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/DSCNet">DSCNet (ICCV'2023)</a> [<a href="https://openaccess.thecvf.com/content/ICCV2023/html/Qi_Dynamic_Snake_Convolution_Based_on_Topological_Geometric_Constraints_for_Tubular_ICCV_2023_paper.html">paper</a>] [<a href="https://github.com/YaoleiQi/DSCNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/EMNet/em_net_model.py">EMNet (MICCAI'2024)</a> [<a href="https://doi.org/10.1007/978-3-031-72114-4_26">paper</a>] [<a href="https://github.com/zang0902/EM-Net">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/MedNeXt/create_mednext_v1.py">MedNeXt (MICCAI'2023)</a> [<a href="https://doi.org/10.1007/978-3-031-43901-8_39">paper</a>] [<a href="https://github.com/MIC-DKFZ/MedNeXt">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/Biformer/model.py">BiFormer (CVPR'2023)</a> [<a href="https://openaccess.thecvf.com/content/CVPR2023/html/Zhu_BiFormer_Vision_Transformer_With_Bi-Level_Routing_Attention_CVPR_2023_paper.html">paper</a>] [<a href="https://github.com/rayleizhu/BiFormer">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/DeBiformer/model.py">DeBiFormer (ACCV'2024)</a> [<a href="https://openaccess.thecvf.com/content/ACCV2024/html/BaoLong_DeBiFormer_Vision_Transformer_with_Deformable_Agent_Bi-level_Routing_Attention_ACCV_2024_paper.html">paper</a>] [<a href="https://github.com/maclong01/DeBiFormer">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/UMamba">UMamba (arXiv'2024)</a> [<a href="
				https://doi.org/10.48550/arXiv.2401.04722">paper</a>] [<a href="https://github.com/bowang-lab/U-Mamba">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/UNeXt">UNeXt (MICCAI'2022)</a> [<a href="https://doi.org/10.1007/978-3-031-16443-9_3">paper</a>] [<a href="https://github.com/jeya-maria-jose/UNeXt-pytorch">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/UXNet3D/network_backbone.py">3D UX-Net (arXiv'2022)</a> [<a href="
				https://doi.org/10.48550/arXiv.2209.15076">paper</a>] [<a href="https://github.com/MASILab/3DUX-Net">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/CCNet/model.py">CCNet (ICCV'2019)</a> [<a href="https://openaccess.thecvf.com/content_ICCV_2019/html/Huang_CCNet_Criss-Cross_Attention_for_Semantic_Segmentation_ICCV_2019_paper.html">paper</a>] [<a href="https://github.com/speedinghzl/CCNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/monai.py">UNETR (WACV'2022)</a> [<a href="https://doi.org/10.1007/978-3-031-08999-2_22">paper</a>] [<a href="https://monai.io/research/unetr">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/UTNet/utnet.py">UTNet (MICCAI'2021)</a> [<a href="https://doi.org/10.1007/978-3-030-87199-4_6">paper</a>] [<a href="https://github.com/yhygao/UTNet">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/monai.py">Swin UNETR (MICCAI workshop'2021)</a> [<a href="https://doi.org/10.1007/978-3-031-08999-2_22">paper</a>] [<a href="https://monai.io/research/swin-unetr">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/monai.py">Swin UNETR-V2 (MICCAI'2023)</a> [<a href="https://doi.org/10.1007/978-3-031-43901-8_40">paper</a>] [<a href="https://monai.io/research/swin-unetr">code</a>]</li>
				<li><a href="nnunet_extend/network_architecture/monai.py">SegResNet (MICCAI workshop'2018)</a> [<a href="https://doi.org/10.1007/978-3-030-11726-9_28">paper</a>] [Code]</li>
				<li><a href="nnunet_extend/network_architecture/monai.py">VNet (3DV'2016)</a> [<a href="https://doi.org/10.1109/3DV.2016.79">paper</a>] [<a href="https://github.com/faustomilletari/VNet">code</a>]</li>
			</ul>
		</td>
		<td>
			<ul>
				<li><a href="nnunet_extend/traning/loss/SuperVoxelLoss/loss.py">SuperVoxelLoss (arXiv_AAAI'2025)</a> [<a href="
				https://doi.org/10.48550/arXiv.2501.01022">paper</a>] [<a href="https://github.com/AllenNeuralDynamics/supervoxel-loss">code</a>]</li>
				<li><a href="nnunet_extend/traning/loss/clDiceLoss.py">clDice (CVPR'2021)</a> [<a href="https://openaccess.thecvf.com/content/CVPR2021/html/Shit_clDice_-_A_Novel_Topology-Preserving_Loss_Function_for_Tubular_Structure_CVPR_2021_paper.html">paper</a>] [<a href="https://github.com/jocpae/clDice">code</a>]</li>
				<li><a href="nnunet_extend/traning/loss/cbDiceLoss.py">cbDice (MICCAI'2024)</a> [<a href="https://doi.org/10.1007/978-3-031-72111-3_5">paper</a>] [<a href="https://github.com/PengchengShi1220/cbDice">code</a>]</li>
				<li><a href="nnunet_extend/traning/loss/SkeletonRecallLoss.py">SkeletonRecall (ECCV'2024)</a> [<a href="https://doi.org/10.1007/978-3-031-72980-5_13">paper</a>] [<a href="https://github.com/MIC-DKFZ/Skeleton-Recall">code</a>]</li>
				<li><a href="nnunet_extend/traning/loss/DropCELoss.py">DropCE (TIP'2021)</a> [<a href="https://doi.org/10.1109/TIP.2021.3125490">paper</a>] [<a href="http://github.com/qiyaolei/Examinee-Examiner-Network">code</a>]</li>
			</ul>
		</td>
		</tr>
  	</tbody>
</table>