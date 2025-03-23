from pathlib import Path

import pandas as pd

from scripts.infer import copy_top_files


def main():
    infer_data_frame = pd.read_csv(Path('inference_results.csv'))
    copy_top_files(infer_data_frame, n=10)


if __name__ == '__main__':
    main()
