import multiprocessing
import shutil
from multiprocessing import Pool

from batchgenerators.utilities.file_and_folder_operations import *

from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw
from skimage import io
from acvl_utils.morphology.morphology_helper import generic_filter_components
from scipy.ndimage import binary_fill_holes
from pathlib import Path
from tqdm import tqdm


def load_and_convert_case(input_image: str, input_seg: str, output_image: str, output_seg: str,
                          min_component_size: int = 50):
    seg = io.imread(input_seg)
    seg[seg == 255] = 1
    image = io.imread(input_image)
    image = image.sum(2)
    mask = image == (3 * 255)
    # the dataset has large white areas in which road segmentations can exist but no image information is available.
    # Remove the road label in these areas
    mask = generic_filter_components(mask, filter_fn=lambda ids, sizes: [i for j, i in enumerate(ids) if
                                                                         sizes[j] > min_component_size])
    mask = binary_fill_holes(mask)
    seg[mask] = 0
    io.imsave(output_seg, seg, check_contrast=False)
    shutil.copy(input_image, output_image)


if __name__ == "__main__":
    # extracted archive from https://www.kaggle.com/datasets/insaff/massachusetts-roads-dataset?resource=download
    source = '/home/yjiang/workspace/fmost/dataset/MassachusettsRoadsDataset'

    dataset_name = 'Dataset120_RoadSegmentation'

    imagestr = join(nnUNet_raw, dataset_name, 'imagesTr')
    imagests = join(nnUNet_raw, dataset_name, 'imagesTs')
    labelstr = join(nnUNet_raw, dataset_name, 'labelsTr')
    labelsts = join(nnUNet_raw, dataset_name, 'labelsTs')
    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)
    maybe_mkdir_p(labelsts)

    train_imgs = subfiles(join(source, 'tiff', 'train'), join=False, suffix='tiff')
    val_imgs = subfiles(join(source, 'tiff', 'val'), join=False, suffix='tiff')
    test_imgs = subfiles(join(source, 'tiff', 'test'), join=False, suffix='tiff')

    num_train = len(train_imgs) + len(val_imgs)

    r = []
    with multiprocessing.get_context("spawn").Pool(multiprocessing.cpu_count()) as p:
        for img in train_imgs:
            r.append(
                p.starmap_async(
                    load_and_convert_case,
                    ((
                        join(source, 'tiff', 'train', img),
                        join(source, 'tiff', 'train_labels', img[:-1]),
                        join(imagestr, img.split('.')[0] + '_0000.tif'),
                        join(labelstr, img.split('.')[0] + '.tif'),
                        50
                     ),)
                )
            )

        for img in val_imgs:
            r.append(
                p.starmap_async(
                    load_and_convert_case,
                    ((
                        join(source, 'tiff', 'val', img),
                        join(source, 'tiff', 'val_labels', img[:-1]),
                        join(imagestr, img.split('.')[0] + '_0000.tif'),
                        join(labelstr, img.split('.')[0] + '.tif'),
                        50
                    ),)
                )
            )

        for img in test_imgs:
            r.append(
                p.starmap_async(
                    load_and_convert_case,
                    ((
                        join(source, 'tiff', 'test', img),
                        join(source, 'tiff', 'test_labels', img[:-1]),
                        join(imagests, img.split('.')[0] + '_0000.tif'),
                        join(labelsts, img.split('.')[0] + '.tif'),
                        50
                    ),)
                )
            )

        for i in tqdm(r):
            i.get()

    generate_dataset_json(join(nnUNet_raw, dataset_name), {0: 'R', 1: 'G', 2: 'B'}, {'background': 0, 'road': 1},
                          num_train, '.tif', dataset_name=dataset_name)
