from pathlib import Path
import pandas as pd
from bokeh.io import show
from bokeh.models import Column
from bokeh.plotting import figure as Figure

from qusi.experimental.application.tess import TessMissionLightCurve


def main():
    data_frame = pd.read_csv('data/extended_info_short_period_variables.csv')
    figures = []
    light_curve_directory = Path('data/spoc_transit_experiment/train/positives/')
    for light_curve_path in list(light_curve_directory.glob('*.fits')):
        tic_id_with_zeros = light_curve_path.name.split("phot_")[1].split("-s")[0]
        my_tic_id = int(tic_id_with_zeros)
        filtered_row = data_frame.loc[data_frame['tic_id'] == my_tic_id]
        curve_period = filtered_row.iloc[0]['period']
        light_curve = TessMissionLightCurve.from_path(light_curve_path)
        light_curve.fold(period=curve_period, epoch=0.0)
        light_curve_figure = Figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
        light_curve_figure.scatter(x=light_curve.folded_times, y=light_curve.fluxes)
        # light_curve_figure.line(x=light_curve.folded_times, y=light_curve.fluxes, line_alpha=0.3)
        figures.append(light_curve_figure)
    column = Column(*figures)
    show(column)



if __name__ == '__main__':
    main()
