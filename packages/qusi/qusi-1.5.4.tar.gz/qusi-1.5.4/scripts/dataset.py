import os
import random
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from qusi.internal.light_curve import LightCurve
from qusi.internal.light_curve_collection import LightCurveObservationCollection
from qusi.internal.light_curve_dataset import LightCurveDataset
from ramjet.photometric_database.tess_two_minute_cadence_light_curve import TessMissionLightCurve
from tqdm import tqdm


def positive_label_function(path):
    return 1


def negative_label_function(path):
    return 0


def get_injectee_paths():
    base_path=Path('data/spoc_transit_experiment/train/negatives')
    injectee_paths_generator = base_path.glob('*.fits')
    injectee_paths = list(injectee_paths_generator)
    return injectee_paths


def get_validation_injectee_paths():
    base_path=Path('data/spoc_transit_experiment/validation/negatives')
    injectee_paths_generator = base_path.glob('*.fits')
    injectee_paths = list(injectee_paths_generator)
    return injectee_paths


def get_injectee_paths2():
    print('Getting light curve paths...')
    base_path = Path('data/tess_light_curves')
    injectee_paths_generator = base_path.glob('**/*.fits')
    paths_limit = 100_000_000
    injectee_paths = []
    for injectee_path_index, injectee_path in enumerate(injectee_paths_generator):
        if injectee_path_index % 10_000 == 0:
            print(f'{injectee_path_index} paths loaded.')
        if injectee_path_index >= paths_limit:
            break
        injectee_paths.append(injectee_path)
    print('Got light curve paths.', flush=True)
    return injectee_paths


def load_times_and_fluxes_from_path(path):
    light_curve = TessMissionLightCurve.from_path(path)
    return light_curve.times, light_curve.fluxes


def check_for_problem_paths(paths):
    with Pool(5) as pool:
        processed = 0
        for _ in pool.imap_unordered(is_problem_path, paths):
            if processed % 100 == 0:
                progress_log_path = Path('progress.txt')
                with progress_log_path.open('w') as progress_log_file:
                    print(processed, flush=True, file=progress_log_file)
            processed += 1


def is_problem_path(path: Path) -> bool:
    try:
        times, fluxes = load_times_and_fluxes_from_path(path)
    except OSError:
        print(f'OSError on: {path}', flush=True)
        return True
    if np.isnan(times).all():
        print(f'All NaN on: {path}', flush=True)
        return True
    return False


def get_heart_train_dataset():
    non_heart_beat_signal_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function=get_non_hb_train,
        load_times_and_fluxes_from_path_function=load_heart_beat_times_and_fluxes_from_path,
        load_label_from_path_function=negative_label_function)
    heart_beat_signal_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function=get_hb_train,
        load_times_and_fluxes_from_path_function=load_heart_beat_times_and_fluxes_from_path,
        load_label_from_path_function=positive_label_function)
    base_tess_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function=get_tess_train,
        load_times_and_fluxes_from_path_function=load_times_and_fluxes_from_path,
        load_label_from_path_function=negative_label_function)
    train_light_curve_dataset = LightCurveDataset.new(
        standard_light_curve_collections=[base_tess_light_curve_collection],
        injectee_light_curve_collections=[base_tess_light_curve_collection],
        injectable_light_curve_collections=[heart_beat_signal_light_curve_collection, non_heart_beat_signal_light_curve_collection],
    )
    return train_light_curve_dataset


def get_heart_validation_dataset():
    non_heart_beat_signal_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function=get_non_hb_validation,
        load_times_and_fluxes_from_path_function=load_heart_beat_times_and_fluxes_from_path,
        load_label_from_path_function=negative_label_function)
    heart_beat_signal_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function = get_hb_validation,
        load_times_and_fluxes_from_path_function=load_heart_beat_times_and_fluxes_from_path,
        load_label_from_path_function=positive_label_function)
    base_tess_light_curve_collection = LightCurveObservationCollection.new(
        get_paths_function = get_tess_validation,
        load_times_and_fluxes_from_path_function=load_times_and_fluxes_from_path,
        load_label_from_path_function=negative_label_function)
    validation_light_curve_dataset = LightCurveDataset.new(
        standard_light_curve_collections=[base_tess_light_curve_collection],
        injectee_light_curve_collections=[base_tess_light_curve_collection],
        injectable_light_curve_collections=[heart_beat_signal_light_curve_collection, non_heart_beat_signal_light_curve_collection],
    )
    return validation_light_curve_dataset


def get_infer_paths():
    return list(Path('data/quick_infer').glob('*.fits'))




def load_heart_beat_times_and_fluxes_from_path(text_file_path):
    data = pd.read_csv(text_file_path, delimiter='\s+', header=None, names=['flux'], skiprows=1)
    flux_list = data['flux'].values
    time_increment_in_day = 10 / (24 * 60)
    increments_in_40_days = int((40 * 24 * 60) / 10)
    times_list_in_days = [i * time_increment_in_day for i in range(increments_in_40_days)]
    times_array = np.arange(len(flux_list), dtype=np.float32) * time_increment_in_day
    light_curve: LightCurve = LightCurve.new(times_array, flux_list)
    return times_array, flux_list


def get_synthetic_heart_beat_signal_paths():
    base_path = 'data/lc_samples'
    heart_beat_paths = []

    for file_name in os.listdir(base_path):
        path_string = os.path.join(base_path, file_name)
        path = Path(path_string)
        if ("fake" not in path.name and 'MassJump' not in path.name and 'TempSwap' not in path.name
                and 'generated_lc_pars' not in path.name):
            heart_beat_paths.append(path)
    random_number_generator = random.Random(0)
    random_number_generator.shuffle(heart_beat_paths)

    return heart_beat_paths


def get_fake_paths():
    base_path = 'data/lc_samples'
    fake_paths = []

    for file_name in os.listdir(base_path):
        path_string = os.path.join(base_path, file_name)
        path = Path(path_string)
        if "fake" in path.name:
            fake_paths.append(path)
    random_number_generator = random.Random(0)
    random_number_generator.shuffle(fake_paths)

    return fake_paths


def get_hb_train():
    paths = get_synthetic_heart_beat_signal_paths()
    return get_train_paths_subset(paths)


def get_non_hb_train():
    paths = get_fake_paths()
    return get_train_paths_subset(paths)


def get_non_hb_validation():
    paths = get_fake_paths()
    return get_validation_paths_subset(paths)


def get_tess_train():
    paths = get_injectee_paths2()
    return get_train_paths_subset(paths)


def get_hb_test():
    paths = get_synthetic_heart_beat_signal_paths()
    return get_test_paths_subset(paths)


def get_tess_test():
    paths = get_injectee_paths2()
    return get_test_paths_subset(paths)


def get_hb_validation():
    paths=get_synthetic_heart_beat_signal_paths()
    return get_validation_paths_subset(paths)


def get_tess_validation():
    paths = get_injectee_paths2()
    return get_validation_paths_subset(paths)


def get_train_paths_subset(paths):
    total_files = len(paths)
    end = int(total_files * 0.8)

    return paths[:end]


def get_validation_paths_subset(paths):
    total_files = len(paths)
    start = int(total_files * 0.8)
    end = int(total_files * 0.9)

    return paths[start:end]


def get_test_paths_subset(paths):
    total_files = len(paths)
    start = int(total_files * 0.9)

    return paths[start:]


if __name__ == '__main__':
    print('Started.', flush=True)
    base_path = Path('data/tess_light_curves')
    injectee_paths_generator = base_path.glob('**/*.fits')
    nan_files = check_for_problem_paths(injectee_paths_generator)
    pass