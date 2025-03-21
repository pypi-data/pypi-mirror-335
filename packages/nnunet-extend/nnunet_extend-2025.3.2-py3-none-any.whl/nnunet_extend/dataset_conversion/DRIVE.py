import multiprocessing
import shutil
from multiprocessing import Pool

from batchgenerators.utilities.file_and_folder_operations import *

from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw
from skimage import io
from pathlib import Path

def load_and_covnert_case(input_image: str, input_seg: str, output_image: str, output_seg: str):
    seg = io.imread(input_seg)[0]
    seg[seg == 255] = 1
    io.imsave(output_seg, seg, check_contrast=False)
    shutil.copy(input_image, output_image)


if __name__ == "__main__":
    root = Path(nnUNet_raw)
    source = '/home/jiangyan/workspace/fmost/dataset/DRIVE'
    source = Path(source)
    dataset_num = 999
    dataset_num = str(dataset_num).zfill(3)
    assert len(dataset_num) == 3
    dataset_name = f'Dataset{dataset_num}_DRIVE'

    imagestr = root / dataset_name / 'imagesTr'
    imagests = root / dataset_name / 'imagesTs'
    labelstr = root / dataset_name / 'labelsTr'
    labelsts = root / dataset_name / 'labelsTs'
    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)
    maybe_mkdir_p(labelsts)

    train_source = source / 'training'
    test_source = source / 'test'   

    valid_ids = list((train_source / '1st_manual').glob(pattern='*.gif'))
    num_train = len(valid_ids)
    for v in valid_ids:
        load_and_covnert_case(
            train_source / 'images' / (v.stem.replace('_manual1', '_training') + '.tif'),
            train_source / '1st_manual' / v.name,
            imagestr / (v.stem.replace('_manual1', '_0000') + '.tif'),
            labelstr / (v.stem.replace('_manual1', '') + '.tif')
        )

    # test
    valid_ids = list((test_source / '1st_manual').glob(pattern='*.gif'))
    for v in valid_ids:
        load_and_covnert_case(
            test_source / 'images' / (v.stem.replace('_manual1', '_test') + '.tif'),
            test_source / '1st_manual' / v.name,
            imagests / (v.stem.replace('_manual1', '_0000') + '.tif'),
            labelsts / (v.stem.replace('_manual1', '') + '.tif')
        )

    generate_dataset_json(root / dataset_name, {0: 'R', 1: 'G', 2: 'B'}, {'background': 0, 'vessel': 1},
                          num_train, '.tif', dataset_name=dataset_name)