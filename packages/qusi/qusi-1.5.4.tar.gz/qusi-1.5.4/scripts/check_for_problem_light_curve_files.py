from torch.utils.data import DataLoader

from qusi.internal.light_curve_collection import LightCurveObservationCollection
from qusi.internal.light_curve_dataset import LightCurveDataset
from scripts.dataset import load_heart_beat_times_and_fluxes_from_path, negative_label_function, get_hb_train, \
    positive_label_function, get_tess_train, load_times_and_fluxes_from_path, get_non_hb_train, get_injectee_paths2


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
        get_paths_function=get_injectee_paths2,
        load_times_and_fluxes_from_path_function=load_times_and_fluxes_from_path,
        load_label_from_path_function=negative_label_function)
    train_light_curve_dataset = LightCurveDataset.new(
        standard_light_curve_collections=[base_tess_light_curve_collection],
        injectee_light_curve_collections=[base_tess_light_curve_collection],
        injectable_light_curve_collections=[heart_beat_signal_light_curve_collection,
                                            non_heart_beat_signal_light_curve_collection],
    )
    return train_light_curve_dataset


def main():
    dataset = get_heart_train_dataset()
    dataloader = DataLoader(dataset, batch_size=1000, pin_memory=True, persistent_workers=True,
                            prefetch_factor=10, num_workers=5)
    batch_count = 0
    for batch_index, batch in enumerate(dataloader):
        batch_count += 1
        print(f'{batch_index * 1000}', flush=True)


if __name__ == '__main__':
    main()
