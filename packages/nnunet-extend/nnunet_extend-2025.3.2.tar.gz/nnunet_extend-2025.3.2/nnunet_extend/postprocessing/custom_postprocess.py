import argparse
import multiprocessing
from nnunetv2.configuration import default_num_processes
from nnunetv2.postprocessing.remove_connected_components import load_postprocess_save
from nnunetv2.utilities.find_class_by_name import recursive_find_python_class
from batchgenerators.utilities.file_and_folder_operations import load_json, subfiles, maybe_mkdir_p, join, isfile, \
    isdir, save_pickle, load_pickle, save_json
import numpy as np
import nnunetv2
from skimage import morphology
from typing import Union, Tuple, List, Callable
from nnunetv2.imageio.reader_writer_registry import determine_reader_writer_from_file_ending

###################### 转二值
def convert_to_binary(segmentation: np.ndarray,
                        threshold: float, 
                        max_value: int,
                        ) -> np.ndarray:
    return np.where(segmentation > threshold, max_value, 0)



def entry_point_convert_to_binary():
    parser = argparse.ArgumentParser('Apples postprocessing specified in pp_pkl_file to input folder.')
    parser.add_argument('-i', type=str, required=True, help='Input folder')
    parser.add_argument('-o', type=str, required=True, help='Output folder')
    parser.add_argument('-np', type=int, required=False, default=default_num_processes,
                        help=f"number of processes to use. Default: {default_num_processes}")
    parser.add_argument('-th', type=float, required=True, help='Threshold for binarization', default=0.5)
    parser.add_argument('-t', type=str, required=True, help='File type to binarize', default='tif')
    parser.add_argument('-rw', type=str, required=False, help='ReaderWriter class to use', default=None)
    parser.add_argument('-v', type=int, required=False, help='Binary Value, default:255', default=255)
    parser.add_argument('--verbose', action='store_true', help="Set this if you like being talked to. You will have "
                                                               "to be a good listener/reader.")
    args = parser.parse_args()
    pp_fn = convert_to_binary
    pp_fn_kwarg = {'threshold': args.th, 'max_value': args.v}
    apply_custom_postprocess(args.i, args.o, args.rw, 
                             pp_fn, pp_fn_kwarg,
                             args.t, args.np, args.verbose)



###################### remove small region
def remove_small_region(segmentation: np.ndarray,
                        min_size: int, 
                        threshold: float, 
                        connectivity: int=2
                        ):
    binary_image = segmentation > threshold
    labeled_image, _ = morphology.label(binary_image, connectivity=connectivity, return_num=True)
    # 移除小于 min_size 的区域
    cleaned_image = morphology.remove_small_objects(labeled_image, min_size=min_size)
    binary_denoised = cleaned_image > 0  # 转为二值掩膜
    denoised_image = segmentation * binary_denoised  # 将原始概率图与去噪后的掩膜相乘，保留概率值
    return denoised_image

def entry_point_remove_small_region():
    parser = argparse.ArgumentParser('Apples postprocessing specified in pp_pkl_file to input folder.')
    parser.add_argument('-i', type=str, required=True, help='Input folder')
    parser.add_argument('-o', type=str, required=True, help='Output folder')
    parser.add_argument('-np', type=int, required=False, default=default_num_processes,
                        help=f"number of processes to use. Default: {default_num_processes}")
    parser.add_argument('-th', type=float, required=True, help='Threshold for binarization', default=0.5)
    parser.add_argument('-t', type=str, required=True, help='File type to binarize', default='tif')
    parser.add_argument('-m', type=int, required=True, help='max small region size', default=300)
    parser.add_argument('-rw', type=str, required=False, help='ReaderWriter class to use', default='NaturalImage2DIO')
    parser.add_argument('--verbose', action='store_true', help="Set this if you like being talked to. You will have "
                                                               "to be a good listener/reader.")
    args = parser.parse_args()
    pp_fn = remove_small_region
    pp_fn_kwarg = {'threshold': args.th, 'min_size': args.m}
    apply_custom_postprocess(args.i, args.o, args.rw, 
                             pp_fn, pp_fn_kwarg,
                             args.t, args.np, args.verbose)

#########################
def apply_custom_postprocess(input_folder: str,
                            output_folder: str,
                            rw: str,
                            pp_fn: Callable,
                            pp_fn_kwarg: dict,
                            file_type:str, 
                            num_processes: int = default_num_processes,
                            verbose: bool=False):
    maybe_mkdir_p(output_folder)
    file_type = "." + file_type
    rw = recursive_find_python_class(join(nnunetv2.__path__[0], "imageio"),
                                                rw, 'nnunetv2.imageio') if rw is not None else determine_reader_writer_from_file_ending(file_type, None, False, True)
    if rw is None:
        raise RuntimeError(f'Unable to locate reader writer class {rw} in nnunetv2.postprocessing. '
                            f'Please place it there (in any .py file)!')
    rw = rw()
    

    with multiprocessing.get_context("spawn").Pool(num_processes) as p:
        files = subfiles(input_folder, suffix=file_type, join=False)
        _ = p.starmap(load_postprocess_save,
                      zip(
                          [join(input_folder, i) for i in files],
                          [join(output_folder, i) for i in files],
                          [rw] * len(files),
                          [[pp_fn]] * len(files),
                          [[pp_fn_kwarg]] * len(files),
                          [verbose] * len(files),
                      )
                      )

if __name__ == '__main__':
    input_folder = '/home/jiangyan/workspace/fmost/dataset/nnUNet/nnUNet_perdict/Dataset201_NeuronSegMixData_dist/nnUNetDistBCETrainer__nnUNetPlans__3d_fullres/fold1'   
    output_folder = '/home/jiangyan/workspace/fmost/dataset/nnUNet/nnUNet_perdict/Dataset201_NeuronSegMixData_dist/nnUNetDistBCETrainer__nnUNetPlans__3d_fullres/fold1_remove_small_region'
    # apply_custom_postprocess(input_folder, output_folder, 'Tiff3DIO', 103, 255, 'tif', default_num_processes, True)
    # pp_fn = convert_to_binary
    # pp_fn_kwarg = {'threshold': 103, 'max_value': 255}
    # apply_custom_postprocess(input_folder, output_folder, 'Tiff3DIO', 
    #                          pp_fn, pp_fn_kwarg,
    #                          'tif', default_num_processes, True)
    pp_fn = remove_small_region
    pp_fn_kwarg = {'threshold': 103, 'min_size':300}
    apply_custom_postprocess(input_folder, output_folder, 'Tiff3DIO', 
                             pp_fn, pp_fn_kwarg,
                             'tif', default_num_processes, True)