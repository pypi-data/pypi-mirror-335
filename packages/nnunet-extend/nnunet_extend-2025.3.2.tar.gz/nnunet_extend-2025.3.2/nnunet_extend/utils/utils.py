import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from batchgenerators.utilities.file_and_folder_operations import load_json, subfiles, maybe_mkdir_p, join, isfile, \
    isdir, save_pickle, load_pickle, save_json
import multiprocessing
from multiprocessing import Pool
from nnunetv2.configuration import default_num_processes
from nnunetv2.utilities.file_path_utilities import get_output_folder
from torch._dynamo import OptimizedModule
import torch
import shutil
import nnunetv2
from nnunetv2.utilities.find_class_by_name import recursive_find_python_class
import os
import tifffile

# '''Swc多树拆分'''
def SplitSwcData(swcData):
    indLs = np.where(swcData[:, -1] == -1)[0].tolist() + [swcData.shape[0]]
    swcDataLs = []
    for i in range(len(indLs) - 1):
        data = swcData[indLs[i]: indLs[i + 1]]
        # 把每个片段的数据的编号修改成从1开始（这个应该要求数据是按顺序的）
        sp = data[0, 0]
        data[:, 0] -= sp - 1
        data[1:, -1] -= sp - 1
        swcDataLs.append(data)
    return swcDataLs


'''获取点云核点云'''
def GetPcKernelPc(pc, kernelArr, imgShape):
    curPc = (pc[:, None] + kernelArr[None]).reshape([-1, 3])
    curPc = np.round(curPc).astype(np.int32)
    curPc[curPc < 0] = 0
    curPc[curPc[:, 2] > imgShape[0] - 1] = imgShape[0] - 1
    curPc[curPc[:, 1] > imgShape[1] - 1] = imgShape[1] - 1
    curPc[curPc[:, 0] > imgShape[2] - 1] = imgShape[2] - 1
    curPc = np.unique(curPc, axis=0)
    return curPc

def SwcToDF(name, save_path, dfImg, minD, maxD, maskMax, kernelLen, kernelArr, imgShape, binary=False):
    swcData = np.loadtxt(name, ndmin=2)
    swcDataLs = SplitSwcData(swcData)
    dfImg[...] = maxD
    for swcData in swcDataLs:
        for ii, item in enumerate(swcData):
            if item[-1] == -1: continue
            p0 = item[2: 5]
            p1 = swcData[int(item[-1]) - 1, 2: 5]
            v = (p1 - p0).reshape([1, 3])
            if np.linalg.norm(v) < 0.1: continue
            # 插值
            d = np.linalg.norm(p0 - p1)
            if d > kernelLen:
                d2 = int(d + 1)
                xLs = (np.arange(1, d2 + 1, 1) / d2).reshape([-1, 1])
                data = p0 * xLs + p1 * (1 - xLs)
            else:
                data = np.array([p0, p1])
            curPc = GetPcKernelPc(data, kernelArr, imgShape)
            proT = (curPc - p0).dot(v.T) / v.dot(v.T)
            proT = np.clip(proT, 0, 1)
            proP = p0 + proT * v
            d = np.linalg.norm(proP - curPc, axis=1)
            if np.isnan(d).any():
                print()
            dfImg[curPc[:, 2], curPc[:, 1], curPc[:, 0]] = np.min([dfImg[curPc[:, 2], curPc[:, 1], curPc[:, 0]], d], axis=0)
        
    dfImg = -np.log(minD + dfImg / maxD * (1- minD))
    dfImg2 = (dfImg / maskMax * 255).astype(np.uint8)
    # dfImg = ((dfImg - dfImg.min()) / (dfImg.max() - dfImg.min()) * 255).astype(np.uint8)
    # dfImg2[dfImg2 < 103] = 0
    if binary:
        dfImg2[dfImg2 < 103] = 0
        dfImg2[dfImg2 >= 103] = 255
    tifffile.imwrite(save_path, dfImg2, compression='lzw')


def entry_point_swc_to_img():
    parser = argparse.ArgumentParser('Compare swc files in two folders.')
    parser.add_argument('-i', type=str, required=True, help='Input folder')
    parser.add_argument('-o', type=str, required=True, help='Output folder')
    parser.add_argument('--b', action='store_true', help='Binary image')
    parser.add_argument('-np', type=int, required=False, default=default_num_processes,
                        help=f"number of processes to use. Default: {default_num_processes}")
    parser.add_argument('--verbose', action='store_true', help="Set this if you like being talked to. You will have "
                                                               "to be a good listener/reader.")
    args = parser.parse_args()

    maybe_mkdir_p(args.o)

    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        inputs = subfiles(args.i, suffix='swc', join=False)
        kernelLen = 3
        imgShape = np.array([256, 256, 256], dtype=np.int32)
        maxD = ((kernelLen ** 2) * 3) ** 0.5
        minD = 0.0697
        maskMax = -np.log(minD)
        dfImg = np.zeros(imgShape[::-1], dtype=np.float32)
        kernelArr = []
        for z in range(-kernelLen, kernelLen + 1):
            for y in range(-kernelLen, kernelLen + 1):
                for x in range(-kernelLen, kernelLen + 1):
                    kernelArr.append([x, y, z])
        results = p.starmap(SwcToDF,
                      zip(
                            [join(args.i, i) for i in inputs],
                            [join(args.o, i.replace('.swc', '.tif')) for i in inputs],
                            [dfImg] * len(inputs),
                            [minD] * len(inputs),
                            [maxD] * len(inputs),
                            [maskMax] * len(inputs),
                            [kernelLen] * len(inputs),
                            [kernelArr] * len(inputs),
                            [imgShape] * len(inputs),
                            [args.b] * len(inputs)
                      )
                      )

        results = pd.DataFrame(results)
        mean = results[['Recall', 'Precision', 'Accuracy', 'F1_Score']].mean()
        mean['FileName'] = 'mean'
        results.loc['mean'] = mean
        results.to_csv(join(args.o, args.n), index=False)
        print('Saved to', join(args.o, args.n))

def swc_distance(swc_1, swc_2, threshold_range=3):
    
    swc_1 = swc_1[['x', 'y', 'z']].sort_values(by='z')
    swc_2 = swc_2[['x', 'y', 'z']].sort_values(by='z')  

    def get_z_dist(x):
        try:
            return swc_2[(swc_2['z'] - x + threshold_range).abs().argmin() : (swc_2['z'] - x - threshold_range).abs().argmin() + 1]
        except:
            return np.inf
    block = swc_1['z'].apply(lambda x: get_z_dist(x))
    return [np.sqrt(((b - line)**2).sum(axis=1)).min() for b, line in zip(block, swc_1.to_numpy())]

def compare_swc(swc_1, swc_2, threshold_radius=6, threshold_range=3, verbose=False):
    filename = Path(swc_1).name
    if verbose:
        print(f"Comparing {filename}...")
    col = ['index', 'type', 'x', 'y', 'z', 'r', 'parent']
    swc_1 = pd.read_csv(swc_1,header=None, sep=' ', names=col)
    swc_2 = pd.read_csv(swc_2,header=None, sep=' ', names=col)
    dist_1_2 = swc_distance(swc_1, swc_2, threshold_range)
    dist_2_1 = swc_distance(swc_2, swc_1, threshold_range)
    TP_trace_index = np.where(np.array(dist_1_2) < threshold_radius)
    TP_gt_index = np.where(np.array(dist_2_1) < threshold_radius)
    FP_index = np.where(np.array(dist_1_2) >= threshold_radius)
    FN_index = np.where(np.array(dist_2_1) >= threshold_radius)
    TP = (len(TP_trace_index[0]) + len(TP_gt_index[0])) / 2
    FP = len(FP_index[0])
    FN = len(FN_index[0])
    TN = 0

    Recall = TP / (TP + FN)
    Precision = TP / (TP + FP)
    Accuracy = (TP + TN) / (TP + TN + FP + FN)
    F1_Score = (2 * Recall * Precision) / (Recall + Precision)
    return {
        'FileName': filename,
        'Recall': Recall,
        'Precision': Precision,
        'Accuracy': Accuracy,
        'F1_Score': F1_Score
    }

def entry_point_compare_swc():
    parser = argparse.ArgumentParser('Compare swc files in two folders.')
    parser.add_argument('input', type=str, help='Input folder')
    parser.add_argument('gt', type=str, help='GroundTruth folder')
    parser.add_argument('-o', type=str, required=True, help='Output folder')
    parser.add_argument('-n', type=str, required=False, help='Name of the output file', default='compare.csv')
    parser.add_argument('-r', type=int, required=False, help='Threshold radius', default=6)
    parser.add_argument('-th', type=int, required=False, help='Threshold range', default=3)
    parser.add_argument('-np', type=int, required=False, default=default_num_processes,
                        help=f"number of processes to use. Default: {default_num_processes}")
    parser.add_argument('--verbose', action='store_true', help="Set this if you like being talked to. You will have "
                                                               "to be a good listener/reader.")
    args = parser.parse_args()

    maybe_mkdir_p(args.o)
    if isfile(join(args.o, args.n)):
        print('File already exists. Exiting...')
        print('Do you want to overwrite? (y/n)')
        if input() != 'y':
            exit(0)

    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        inputs = subfiles(args.input, suffix='swc', join=False)
        gts = subfiles(args.gt, suffix='swc', join=False)
        assert len(inputs) == len(gts), f'Number of files in input {len(inputs)} and gt {len(gts)} do not match.'
        results = p.starmap(compare_swc,
                      zip(
                            [join(args.input, i) for i in inputs],
                            [join(args.gt, i) for i in gts],
                            [args.r] * len(inputs),
                            [args.th] * len(inputs),
                            [args.verbose] * len(inputs)
                      )
                      )

        results = pd.DataFrame(results)
        mean = results[['Recall', 'Precision', 'Accuracy', 'F1_Score']].mean()
        mean['FileName'] = 'mean'
        results.loc['mean'] = mean
        results.to_csv(join(args.o, args.n), index=False)
        print('Saved to', join(args.o, args.n))



def rename_files(path, suffix='tif', channels=0, mode='add', verbose=False):
    suffix = f'.{suffix}'
    path = Path(path)
    if verbose:
        print(f'Rename {path.name}...')
    if mode=='add':
        new_suffix = f'_{str(channels).zfill(4)}{suffix}'
        if path.name.endswith(new_suffix):
            return
        path.rename(path.with_name(path.name.replace(suffix, '_' + str(channels).zfill(4) + suffix)))
    else:
        path.rename(path.with_name(path.name.replace('_' + str(channels).zfill(4) + suffix, suffix)))

def entry_point_rename():
    parser = argparse.ArgumentParser('Rename image files in a folder.')
    parser.add_argument('-i', type=str, help='Input folder')
    parser.add_argument('-t', type=str, help='Image type', default='tif')
    parser.add_argument('-c', type=int, help='channels', default=0)
    parser.add_argument('-m', type=str, help='rename mode, add or sub', default='add')
    parser.add_argument('-np', type=int, required=False, default=default_num_processes,
                        help=f"number of processes to use. Default: {default_num_processes}")
    parser.add_argument('--verbose', action='store_true', help="Set this if you like being talked to. You will have "
                                                               "to be a good listener/reader.")
    args = parser.parse_args()

    assert args.m in ['add', 'sub'], f"Invalid mode '{args.m}' provided. Expected 'add' or 'sub'."

    with multiprocessing.get_context("spawn").Pool(args.np) as p:
        inputs = subfiles(args.i, suffix=args.t, join=False)
        print('Found {} {} files in the input folder.'.format(len(inputs), args.t))
        assert len(inputs) != 0, 'No {} files found in the input folder.'.format(args.t)
        _ = p.starmap(rename_files,
                      zip(
                            [join(args.i, i) for i in inputs],
                            [args.t] * len(inputs),
                            [args.c] * len(inputs),
                            [args.m] * len(inputs),
                            [args.verbose] * len(inputs)
                      )
                    )

        print(f'Rename {len(inputs)} files in input folder {args.i} Done!')


###################### 保存模型+权重的pth
def entry_point_save_model_with_weight():
    parser = argparse.ArgumentParser(description='保存模型和权重')
    parser.add_argument('-o', type=str, required=True,
                        help='Output folder.')
    parser.add_argument('-d', type=str, required=True,
                        help='Dataset with which you would like to predict. You can specify either dataset name or id')
    parser.add_argument('-p', type=str, required=False, default='nnUNetPlans',
                        help='Plans identifier. Specify the plans in which the desired configuration is located. '
                             'Default: nnUNetPlans')
    parser.add_argument('-tr', type=str, required=False, default='nnUNetTrainer',
                        help='What nnU-Net trainer class was used for training? Default: nnUNetTrainer')
    parser.add_argument('-c', type=str, required=True,
                        help='nnU-Net configuration that should be used for prediction. Config must be located '
                             'in the plans specified with -p')
    parser.add_argument('-f', nargs='+', type=str, required=False, default=(0, 1, 2, 3, 4),
                        help='Specify the folds of the trained model that should be used for prediction. '
                             'Default: (0, 1, 2, 3, 4)')
    parser.add_argument('-chk', type=str, required=False, default='checkpoint_final.pth',
                        help='Name of the checkpoint you want to use. Default: checkpoint_final.pth')
    # custom_predictor
    parser.add_argument('-cp', type=str, required=False, default='nnUNetPredictor',
                        help='Custom predictor class. Default: nnUNetPredictor')

    print(
        "\n#######################################################################\nPlease cite the following paper "
        "when using nnU-Net:\n"
        "Isensee, F., Jaeger, P. F., Kohl, S. A., Petersen, J., & Maier-Hein, K. H. (2021). "
        "nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation. "
        "Nature methods, 18(2), 203-211.\n#######################################################################\n")

    args = parser.parse_args()
    args.f = [i if i == 'all' else int(i) for i in args.f]

    model_folder = get_output_folder(args.d, args.tr, args.p, args.c)

    if not isdir(args.o):
        maybe_mkdir_p(args.o)

    # custom predictor
    predictor_name = args.cp
    predictor_class = recursive_find_python_class(join(nnunetv2.__path__[0], "inference"), predictor_name, 'nnunetv2.inference')

    if predictor_class is None:
        raise RuntimeError(f'Unable to locate predictor class {predictor_name} in nnunetv2.inference. '
                            f'Please place it there (in any .py file)!')
    
    predictor = predictor_class(tile_step_size=0.5,
                                use_gaussian=True,
                                use_mirroring=False,
                                perform_everything_on_device=True,
                                device=torch.device('cpu'),
                                verbose=False,
                                verbose_preprocessing=False,
                                allow_tqdm=False)
    predictor.initialize_from_trained_model_folder(
        model_folder,
        args.f,
        checkpoint_name=args.chk
    )

    for params in predictor.list_of_parameters:
        # messing with state dict names...
        if not isinstance(predictor.network, OptimizedModule):
            predictor.network.load_state_dict(params)
        else:
            predictor.network._orig_mod.load_state_dict(params)

    checkpoint = torch.load(join(model_folder, f'fold_{args.f[0]}', args.chk),
                                    map_location=torch.device('cpu'), weights_only=False)
    checkpoint['network_weights'] = predictor.network
    torch.save(checkpoint, join(args.o, args.chk))
    print(f'save model with weights to f{join(args.o, args.chk)}')
    shutil.copy(join(model_folder, 'dataset.json'), join(args.o, 'dataset.json'))
    shutil.copy(join(model_folder, 'plans.json'), join(args.o, 'plans.json'))