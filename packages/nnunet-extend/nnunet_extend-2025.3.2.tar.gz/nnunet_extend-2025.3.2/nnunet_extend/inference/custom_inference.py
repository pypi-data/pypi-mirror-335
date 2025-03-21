from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor as nnUNetPredictorBase
import inspect
import multiprocessing
import os
from copy import deepcopy
from time import sleep
from typing import Tuple, Union, List

import numpy as np
import torch
from batchgenerators.dataloading.multi_threaded_augmenter import MultiThreadedAugmenter
from batchgenerators.utilities.file_and_folder_operations import load_json, join, maybe_mkdir_p, save_json

from nnunetv2.configuration import default_num_processes
from nnunetv2.inference.data_iterators import PreprocessAdapterFromNpy
from nnunetv2.inference.export_prediction import convert_predicted_logits_to_segmentation_with_correct_shape
from nnunetv2.inference.sliding_window_prediction import compute_gaussian
from nnunetv2.utilities.file_path_utilities import check_workers_alive_and_busy
from nnunetv2.utilities.helpers import empty_cache
from nnunetv2.utilities.json_export import recursive_fix_for_json_export
from nnunetv2.utilities.plans_handling.plans_handler import PlansManager, ConfigurationManager
from nnunetv2.utilities.label_handling.label_handling import LabelManager
from batchgenerators.utilities.file_and_folder_operations import load_json, save_pickle
from nnunetv2.utilities.label_handling.label_handling import determine_num_input_channels
from nnunet_extend.registry.registry import INFERENCES, TRAINERS
from torch._dynamo import OptimizedModule
import nnunet_extend

def export_prediction_from_logits(predicted_array_or_file: Union[np.ndarray, torch.Tensor], properties_dict: dict,
                                  configuration_manager: ConfigurationManager,
                                  plans_manager: PlansManager,
                                  dataset_json_dict_or_file: Union[dict, str], output_file_truncated: str,
                                  save_probabilities: bool = False,
                                  num_threads_torch: int = default_num_processes):
    # if isinstance(predicted_array_or_file, str):
    #     tmp = deepcopy(predicted_array_or_file)
    #     if predicted_array_or_file.endswith('.npy'):
    #         predicted_array_or_file = np.load(predicted_array_or_file)
    #     elif predicted_array_or_file.endswith('.npz'):
    #         predicted_array_or_file = np.load(predicted_array_or_file)['softmax']
    #     os.remove(tmp)

    if isinstance(dataset_json_dict_or_file, str):
        dataset_json_dict_or_file = load_json(dataset_json_dict_or_file)

    label_manager = plans_manager.get_label_manager(dataset_json_dict_or_file)
    ret = convert_predicted_logits_to_segmentation_with_correct_shape(
        predicted_array_or_file, plans_manager, configuration_manager, label_manager, properties_dict,
        return_probabilities=save_probabilities, num_threads_torch=num_threads_torch
    )
    del predicted_array_or_file

    # save
    if save_probabilities:
        segmentation_final, probabilities_final = ret
        np.savez_compressed(output_file_truncated + '.npz', probabilities=probabilities_final)
        save_pickle(properties_dict, output_file_truncated + '.pkl')
        del probabilities_final, ret
    else:
        segmentation_final = ret
        del ret

    rw = plans_manager.image_reader_writer_class()
    rw.write_seg(segmentation_final*255, output_file_truncated + dataset_json_dict_or_file['file_ending'],
                 properties_dict)

@INFERENCES.register_module()
class nnUNetPredictor(nnUNetPredictorBase):
    def initialize_from_trained_model_folder(self, model_training_output_dir: str,
                                             use_folds: Union[Tuple[Union[int, str]], None],
                                             checkpoint_name: str = 'checkpoint_final.pth'):
        """
        This is used when making predictions with a trained model
        """
        if use_folds is None:
            use_folds = nnUNetPredictor.auto_detect_available_folds(model_training_output_dir, checkpoint_name)

        dataset_json = load_json(join(model_training_output_dir, 'dataset.json'))
        plans = load_json(join(model_training_output_dir, 'plans.json'))
        plans_manager = PlansManager(plans)

        if isinstance(use_folds, str):
            use_folds = [use_folds]

        parameters = []
        for i, f in enumerate(use_folds):
            f = int(f) if f != 'all' else f
            checkpoint = torch.load(join(model_training_output_dir, f'fold_{f}', checkpoint_name),
                                    map_location=torch.device('cpu'), weights_only=False)
            if i == 0:
                trainer_name = checkpoint['trainer_name']
                configuration_name = checkpoint['init_args']['configuration']
                inference_allowed_mirroring_axes = checkpoint['inference_allowed_mirroring_axes'] if \
                    'inference_allowed_mirroring_axes' in checkpoint.keys() else None

            parameters.append(checkpoint['network_weights'])

        configuration_manager = plans_manager.get_configuration(configuration_name)
        # restore network
        num_input_channels = determine_num_input_channels(plans_manager, configuration_manager, dataset_json)
        trainer_class = TRAINERS.get(trainer_name)

        if trainer_class is None:
            raise RuntimeError(f'Unable to locate trainer class {trainer_name} in nnunet_extend.training.trainers. '
                               f'Please place it there (in any .py file)!')
        network = trainer_class.build_network_architecture(
            configuration_manager.network_arch_class_name,
            configuration_manager.network_arch_init_kwargs,
            configuration_manager.network_arch_init_kwargs_req_import,
            num_input_channels,
            plans_manager.get_label_manager(dataset_json).num_segmentation_heads,
            enable_deep_supervision=False
        )

        self.plans_manager = plans_manager
        self.configuration_manager = configuration_manager
        self.list_of_parameters = parameters

        # initialize network with first set of parameters, also see https://github.com/MIC-DKFZ/nnUNet/issues/2520
        try:
            network.load_state_dict(parameters[0])
        except: 
            print('Failed to load state dict. If you want to load state dict with strict=False?')
            if input().lower() in ('yes', 'y', '1', 'true', 't'):
                network.load_state_dict(parameters[0], strict=False)
            else:
                raise RuntimeError('Failed to load state dict. Exiting...')

        self.network = network
        self.dataset_json = dataset_json
        self.trainer_name = trainer_name
        self.allowed_mirroring_axes = inference_allowed_mirroring_axes
        self.label_manager = plans_manager.get_label_manager(dataset_json)
        if ('nnUNet_compile' in os.environ.keys()) and (os.environ['nnUNet_compile'].lower() in ('true', '1', 't')) \
                and not isinstance(self.network, OptimizedModule):
            print('Using torch.compile')
            self.network = torch.compile(self.network)

@INFERENCES.register_module()
class nnUNetPredictorBinary(nnUNetPredictor):
    def predict_from_data_iterator(self,
                                   data_iterator,
                                   save_probabilities: bool = False,
                                   num_processes_segmentation_export: int = default_num_processes):
        """
        each element returned by data_iterator must be a dict with 'data', 'ofile' and 'data_properties' keys!
        If 'ofile' is None, the result will be returned instead of written to a file
        """
        with multiprocessing.get_context("spawn").Pool(num_processes_segmentation_export) as export_pool:
            worker_list = [i for i in export_pool._pool]
            r = []
            for preprocessed in data_iterator:
                data = preprocessed['data']
                if isinstance(data, str):
                    delfile = data
                    data = torch.from_numpy(np.load(data))
                    os.remove(delfile)

                ofile = preprocessed['ofile']
                if ofile is not None:
                    print(f'\nPredicting {os.path.basename(ofile)}:')
                else:
                    print(f'\nPredicting image of shape {data.shape}:')

                print(f'perform_everything_on_device: {self.perform_everything_on_device}')

                properties = preprocessed['data_properties']

                # let's not get into a runaway situation where the GPU predicts so fast that the disk has to b swamped with
                # npy files
                proceed = not check_workers_alive_and_busy(export_pool, worker_list, r, allowed_num_queued=2)
                while not proceed:
                    sleep(0.1)
                    proceed = not check_workers_alive_and_busy(export_pool, worker_list, r, allowed_num_queued=2)

                prediction = self.predict_logits_from_preprocessed_data(data).cpu()

                if ofile is not None:
                    # this needs to go into background processes
                    # export_prediction_from_logits(prediction, properties, self.configuration_manager, self.plans_manager,
                    #                               self.dataset_json, ofile, save_probabilities)
                    print('sending off prediction to background worker for resampling and export')
                    r.append(
                        export_pool.starmap_async(
                            export_prediction_from_logits,
                            ((prediction, properties, self.configuration_manager, self.plans_manager,
                              self.dataset_json, ofile, save_probabilities),)
                        )
                    )
                else:
                    # convert_predicted_logits_to_segmentation_with_correct_shape(
                    #             prediction, self.plans_manager,
                    #              self.configuration_manager, self.label_manager,
                    #              properties,
                    #              save_probabilities)

                    print('sending off prediction to background worker for resampling')
                    r.append(
                        export_pool.starmap_async(
                            convert_predicted_logits_to_segmentation_with_correct_shape, (
                                (prediction, self.plans_manager,
                                 self.configuration_manager, self.label_manager,
                                 properties,
                                 save_probabilities),)
                        )
                    )
                if ofile is not None:
                    print(f'done with {os.path.basename(ofile)}')
                else:
                    print(f'\nDone with image of shape {data.shape}:')
            ret = [i.get()[0] for i in r]

        if isinstance(data_iterator, MultiThreadedAugmenter):
            data_iterator._finish()

        # clear lru cache
        compute_gaussian.cache_clear()
        # clear device cache
        empty_cache(self.device)
        return ret
    
    def predict_single_npy_array(self, input_image: np.ndarray, image_properties: dict,
                                 segmentation_previous_stage: np.ndarray = None,
                                 output_file_truncated: str = None,
                                 save_or_return_probabilities: bool = False):
        """
        WARNING: SLOW. ONLY USE THIS IF YOU CANNOT GIVE NNUNET MULTIPLE IMAGES AT ONCE FOR SOME REASON.


        input_image: Make sure to load the image in the way nnU-Net expects! nnU-Net is trained on a certain axis
                     ordering which cannot be disturbed in inference,
                     otherwise you will get bad results. The easiest way to achieve that is to use the same I/O class
                     for loading images as was used during nnU-Net preprocessing! You can find that class in your
                     plans.json file under the key "image_reader_writer". If you decide to freestyle, know that the
                     default axis ordering for medical images is the one from SimpleITK. If you load with nibabel,
                     you need to transpose your axes AND your spacing from [x,y,z] to [z,y,x]!
        image_properties must only have a 'spacing' key!
        """
        ppa = PreprocessAdapterFromNpy([input_image], [segmentation_previous_stage], [image_properties],
                                       [output_file_truncated],
                                       self.plans_manager, self.dataset_json, self.configuration_manager,
                                       num_threads_in_multithreaded=1, verbose=self.verbose)
        if self.verbose:
            print('preprocessing')
        dct = next(ppa)

        if self.verbose:
            print('predicting')
        predicted_logits = self.predict_logits_from_preprocessed_data(dct['data']).cpu()

        if self.verbose:
            print('resampling to original shape')
        if output_file_truncated is not None:
            export_prediction_from_logits(predicted_logits, dct['data_properties'], self.configuration_manager,
                                          self.plans_manager, self.dataset_json, output_file_truncated,
                                          save_or_return_probabilities)
        else:
            ret = convert_predicted_logits_to_segmentation_with_correct_shape(predicted_logits, self.plans_manager,
                                                                              self.configuration_manager,
                                                                              self.label_manager,
                                                                              dct['data_properties'],
                                                                              return_probabilities=
                                                                              save_or_return_probabilities)
            if save_or_return_probabilities:
                return ret[0], ret[1]
            else:
                return ret
            
    def predict_from_files_sequential(self,
                           list_of_lists_or_source_folder: Union[str, List[List[str]]],
                           output_folder_or_list_of_truncated_output_files: Union[str, None, List[str]],
                           save_probabilities: bool = False,
                           overwrite: bool = True,
                           folder_with_segs_from_prev_stage: str = None):
        """
        Just like predict_from_files but doesn't use any multiprocessing. Slow, but sometimes necessary
        """
        if isinstance(output_folder_or_list_of_truncated_output_files, str):
            output_folder = output_folder_or_list_of_truncated_output_files
        elif isinstance(output_folder_or_list_of_truncated_output_files, list):
            output_folder = os.path.dirname(output_folder_or_list_of_truncated_output_files[0])
            if len(output_folder) == 0:  # just a file was given without a folder
                output_folder = os.path.curdir
        else:
            output_folder = None

        ########################
        # let's store the input arguments so that its clear what was used to generate the prediction
        if output_folder is not None:
            my_init_kwargs = {}
            for k in inspect.signature(self.predict_from_files_sequential).parameters.keys():
                my_init_kwargs[k] = locals()[k]
            my_init_kwargs = deepcopy(
                my_init_kwargs)  # let's not unintentionally change anything in-place. Take this as a
            recursive_fix_for_json_export(my_init_kwargs)
            save_json(my_init_kwargs, join(output_folder, 'predict_from_raw_data_args.json'))

            # we need these two if we want to do things with the predictions like for example apply postprocessing
            save_json(self.dataset_json, join(output_folder, 'dataset.json'), sort_keys=False)
            save_json(self.plans_manager.plans, join(output_folder, 'plans.json'), sort_keys=False)
        #######################

        # check if we need a prediction from the previous stage
        if self.configuration_manager.previous_stage_name is not None:
            assert folder_with_segs_from_prev_stage is not None, \
                f'The requested configuration is a cascaded network. It requires the segmentations of the previous ' \
                f'stage ({self.configuration_manager.previous_stage_name}) as input. Please provide the folder where' \
                f' they are located via folder_with_segs_from_prev_stage'

        # sort out input and output filenames
        list_of_lists_or_source_folder, output_filename_truncated, seg_from_prev_stage_files = \
            self._manage_input_and_output_lists(list_of_lists_or_source_folder,
                                                output_folder_or_list_of_truncated_output_files,
                                                folder_with_segs_from_prev_stage, overwrite, 0, 1,
                                                save_probabilities)
        if len(list_of_lists_or_source_folder) == 0:
            return

        label_manager = self.plans_manager.get_label_manager(self.dataset_json)
        preprocessor = self.configuration_manager.preprocessor_class(verbose=self.verbose)

        if output_filename_truncated is None:
            output_filename_truncated = [None] * len(list_of_lists_or_source_folder)
        if seg_from_prev_stage_files is None:
            seg_from_prev_stage_files = [None] * len(seg_from_prev_stage_files)

        ret = []
        for li, of, sps in zip(list_of_lists_or_source_folder, output_filename_truncated, seg_from_prev_stage_files):
            data, seg, data_properties = preprocessor.run_case(
                li,
                sps,
                self.plans_manager,
                self.configuration_manager,
                self.dataset_json
            )

            print(f'perform_everything_on_device: {self.perform_everything_on_device}')

            prediction = self.predict_logits_from_preprocessed_data(torch.from_numpy(data)).cpu()

            if of is not None:
                export_prediction_from_logits(prediction, data_properties, self.configuration_manager, self.plans_manager,
                  self.dataset_json, of, save_probabilities)
            else:
                ret.append(convert_predicted_logits_to_segmentation_with_correct_shape(prediction, self.plans_manager,
                     self.configuration_manager, self.label_manager,
                     data_properties,
                     save_probabilities))

        # clear lru cache
        compute_gaussian.cache_clear()
        # clear device cache
        empty_cache(self.device)
        return ret