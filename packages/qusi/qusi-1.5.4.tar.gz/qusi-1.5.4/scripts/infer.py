import datetime
import shutil
from pathlib import Path

import pandas as pd
import torch

from qusi.data import FiniteStandardLightCurveDataset, LightCurveCollection
from qusi.model import Hadryss
from qusi.session import get_device, infer_session
from qusi.internal.logging import set_up_default_logger

from scripts.custom_model import TwoConOneDense
from scripts.dataset import load_times_and_fluxes_from_path, get_infer_paths, get_injectee_paths2


def main():
    print(f'Python script started.', flush=True)
    infer_light_curve_collection = LightCurveCollection.new(
        get_paths_function=get_injectee_paths2,
        load_times_and_fluxes_from_path_function=load_times_and_fluxes_from_path)

    test_light_curve_dataset = FiniteStandardLightCurveDataset.new(
       light_curve_collections=[infer_light_curve_collection])

    model = Hadryss.new()
    device = get_device()
    state_dict = torch.load('sessions/w8d71q24_latest_model.pt', map_location=device)
    for key in list(state_dict.keys()):
        state_dict[key.replace('prediction_layer.', 'end_module.prediction_layer.')] = state_dict.pop(key)
    model.load_state_dict(state_dict)
    set_up_default_logger()
    confidences = infer_session(infer_datasets=[test_light_curve_dataset], model=model,
                                batch_size=1000, device=device, workers_per_dataloader=5)[0]
    paths = list(get_injectee_paths2())
    data_frame = pd.DataFrame(data={
        'path': paths,
        'confidence': confidences
    })
    copy_top_files(data_frame)
    datetime_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    data_frame.to_csv(f'inference_results_{datetime_string}.csv')
    # sorted_paths_with_confidences = sorted(
    #     paths_with_confidences, key=lambda path_with_confidence: path_with_confidence[1], reverse=True)
    # print(sorted_paths_with_confidences)
    #
    # with open('sorted_paths_with_confidences.txt', 'w') as file:
    #     for path, confidence in sorted_paths_with_confidences:
    #         file.write(f'{path}: {confidence}\n')


def copy_top_files(data_frame, n=100):
    sorted_data_frame = data_frame.sort_values(by='confidence', ascending=False)
    top_files = sorted_data_frame.head(n)
    destination_directory = Path('data/top_files_copied')
    destination_directory.mkdir(exist_ok=True)
    for path in top_files['path']:
        file_to_copy = Path(path)
        destination = Path(destination_directory / file_to_copy.name)
        shutil.copy(file_to_copy, destination)


if __name__ == '__main__':
    main()
