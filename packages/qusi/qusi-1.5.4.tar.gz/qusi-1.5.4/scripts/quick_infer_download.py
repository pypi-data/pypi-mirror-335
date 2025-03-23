from pathlib import Path

from ramjet.data_interface.tess_data_interface import download_spoc_light_curves_for_tic_ids

sectors = list(range(27, 56))

download_spoc_light_curves_for_tic_ids(
    tic_ids=[150284425],
    download_directory=Path('data/spoc_transit_experiment/quick_infer_test'),
    sectors=sectors,
    limit=1)

download_spoc_light_curves_for_tic_ids(
    tic_ids=[441626681],
    download_directory=Path('data/spoc_transit_experiment/quick_infer_test'),
    sectors=sectors,
    limit=1)

download_spoc_light_curves_for_tic_ids(
    tic_ids=[277236190],
    download_directory=Path('data/spoc_transit_experiment/quick_infer_test'),
    sectors=sectors,
    limit=1)
