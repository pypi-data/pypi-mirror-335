import multiprocessing
import shutil
from multiprocessing import Pool

from batchgenerators.utilities.file_and_folder_operations import *

from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import json
import multiprocessing
import shutil
from multiprocessing import Pool

labels = {
    'background': 0, 'wall': 1, 'building': 2, 'sky': 3, 'floor': 4, 'tree': 5, 'ceiling': 6, 'road': 7,
    'bed ': 8, 'windowpane': 9, 'grass': 10, 'cabinet': 11, 'sidewalk': 12,
    'person': 13, 'earth': 14, 'door': 15, 'table': 16, 'mountain': 17, 'plant': 18,
    'curtain': 19, 'chair': 20, 'car': 21, 'water': 22, 'painting': 23, 'sofa': 24,
    'shelf': 25, 'house': 26, 'sea': 27, 'mirror': 28, 'rug': 29, 'field': 30, 'armchair': 31,
    'seat': 32, 'fence': 33, 'desk': 34, 'rock': 35, 'wardrobe': 36, 'lamp': 37,
    'bathtub': 38, 'railing': 39, 'cushion': 40, 'base': 41, 'box': 42, 'column': 43,
    'signboard': 44, 'chest of drawers': 45, 'counter': 46, 'sand': 47, 'sink': 48,
    'skyscraper': 49, 'fireplace': 50, 'refrigerator': 51, 'grandstand': 52,
    'path': 53, 'stairs': 54, 'runway': 55, 'case': 56, 'pool table': 57, 'pillow': 58,
    'screen door': 59, 'stairway': 60, 'river': 61, 'bridge': 62, 'bookcase': 63,
    'blind': 64, 'coffee table': 65, 'toilet': 66, 'flower': 67, 'book': 68, 'hill': 69,
    'bench': 70, 'countertop': 71, 'stove': 72, 'palm': 73, 'kitchen island': 74,
    'computer': 75, 'swivel chair': 76, 'boat': 77, 'bar': 78, 'arcade machine': 79,
    'hovel': 80, 'bus': 81, 'towel': 82, 'light': 83, 'truck': 84, 'tower': 85,
    'chandelier': 86, 'awning': 87, 'streetlight': 88, 'booth': 89,
    'television receiver': 90, 'airplane': 91, 'dirt track': 92, 'apparel': 93,
    'pole': 94, 'land': 95, 'bannister': 96, 'escalator': 97, 'ottoman': 98, 'bottle': 99,
    'buffet': 100, 'poster': 101, 'stage': 102, 'van': 103, 'ship': 104, 'fountain': 105,
    'conveyer belt': 106, 'canopy': 107, 'washer': 108, 'plaything': 109,
    'swimming pool': 110, 'stool': 111, 'barrel': 112, 'basket': 113, 'waterfall': 114,
    'tent': 115, 'bag': 116, 'minibike': 117, 'cradle': 118, 'oven': 119, 'ball': 120, 'food': 121,
    'step': 122, 'tank': 123, 'trade name': 124, 'microwave': 125, 'pot': 126, 'animal': 127,
    'bicycle': 128, 'lake': 129, 'dishwasher': 130, 'screen': 131, 'blanket': 132,
    'sculpture': 133, 'hood': 134, 'sconce': 135, 'vase': 136, 'traffic light': 137,
    'tray': 138, 'ashcan': 139, 'fan': 140, 'pier': 141, 'crt screen': 142, 'plate': 143,
    'monitor': 144, 'bulletin board': 145, 'shower': 146, 'radiator': 147, 'glass': 148,
    'clock': 149, 'flag': 150
}

def load_and_covnert_case(input_image: str, input_seg: str, output_image: str, output_seg: str):
    Image.open(input_image).convert('RGB').save(output_image)
    shutil.copy(input_seg, output_seg)



if __name__ == "__main__":
    root = Path(nnUNet_raw)
    source = '/home/yjiang/workspace/local/dataset/ADEChallengeData2016'
    source = Path(source)
    dataset_num = 998
    dataset_num = str(dataset_num).zfill(3)
    assert len(dataset_num) == 3
    dataset_name = f'Dataset{dataset_num}_ADE20K'

    imagestr = root / dataset_name / 'imagesTr'
    imagests = root / dataset_name / 'imagesTs'
    labelstr = root / dataset_name / 'labelsTr'
    labelsts = root / dataset_name / 'labelsTs'
    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)
    maybe_mkdir_p(labelsts)

    
    train_imgs = list((source / 'images' / 'training').glob(pattern='*.jpg'))
    val_imgs = list((source / 'images' / 'validation').glob(pattern='*.jpg'))
    train_annotaions = list((source / 'annotations' / 'training').glob(pattern='*.png'))
    val_annotaions = list((source / 'annotations' / 'validation').glob(pattern='*.png'))

    split = {
        'train': [i.stem for i in train_imgs],
        'val': [i.stem for i in val_imgs]
    }

    num_train = len(train_imgs) + len(val_imgs)

    generate_dataset_json(root / dataset_name, {0: 'R', 1: 'G', 2: 'B'}, labels,
                          num_train, '.png', dataset_name=dataset_name)
    
    with open(root / dataset_name / 'split.json', 'w') as f:
        json.dump(split, f)

    r = []
    with multiprocessing.get_context("spawn").Pool(multiprocessing.cpu_count()) as p:
        for img, anno in zip(train_imgs, train_annotaions):
            r.append(
                p.starmap_async(
                    load_and_covnert_case,
                    ((
                        img,
                        anno,
                        imagestr / f'{img.stem}_0000.png',
                        labelstr / anno.name,
                     ),)
                )
            )

        for img, anno in zip(val_imgs, val_annotaions):
            r.append(
                p.starmap_async(
                    load_and_covnert_case,
                    ((
                        img,
                        anno,
                        imagestr / f'{img.stem}_0000.png',
                        labelstr / anno.name,
                    ),)
                )
            )

        for i in tqdm(r):
            i.get()
