import pandas as pd
from astropy import units
import lightkurve as lk
import csv

from bokeh.models import Column, Div
from lightkurve.periodogram import BoxLeastSquaresPeriodogram

import numpy as np
from pathlib import Path
from astropy.timeseries import LombScargle
from bokeh.io import save

from bokeh.io import show
from bokeh.plotting import figure

from qusi.internal.light_curve import LightCurve, remove_nan_flux_data_points_from_light_curve
from qusi.internal.light_curve_dataset import inject_light_curve
from qusi.internal.light_curve_observation import LightCurveObservation
from ramjet.photometric_database.tess_two_minute_cadence_light_curve import TessMissionLightCurve

from scripts.dataset import load_heart_beat_times_and_fluxes_from_path, load_times_and_fluxes_from_path


def plottingTheTopConfidences():
        possible_heart_beat_paths = ['']
        light_curve_figures = []
        text_file_path = Path('inference_results.csv')
        data_frame = pd.read_csv(text_file_path)
        for i, row in data_frame.iterrows():
            if i < 10:
                file_path = row['path']
                path = Path(file_path)
                times, fluxes = load_times_and_fluxes_from_path(path)
                light_curve = LightCurve.new(times, fluxes)
                light_curve = remove_nan_flux_data_points_from_light_curve(light_curve)
                light_curve_fig = figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
                light_curve_fig.scatter(x=light_curve.times, y=light_curve.fluxes)
                light_curve_fig.line(x=light_curve.times, y=light_curve.fluxes,
                                 line_alpha=0.3)
                light_curve_fig.sizing_mode = 'stretch_width'
                light_curve_figures.append(Div(text=str(path)))
                light_curve_figures.append(light_curve_fig)
            else:
                break
        column = Column(*light_curve_figures)
        column.sizing_mode = 'stretch_width'
        show(column)



def main():
    # synthetic_heart_beat_paths = get_synthetic_heart_beat_signal_paths()
    # print(synthetic_heart_beat_paths)
    all_combined_figures = []
    synthetic_heart_beat_paths = ['']
    for i, text_file_path in enumerate(synthetic_heart_beat_paths[:1]):
        text_file_path = Path('data/lc_samples/generated_lc_000003.txt')
        times, fluxes = load_heart_beat_times_and_fluxes_from_path(text_file_path)
        light_curve = LightCurve.new(times, fluxes)
        # light_curve: LightCurve = LightCurve.new(data['time'], data['flux'])
        # light_curve_figure = figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
        # light_curve_figure.scatter(x=light_curve.times, y=light_curve.fluxes)
        # show(light_curve_figure)

        injectable_light_curve = light_curve
        injectable_light_curve = remove_nan_flux_data_points_from_light_curve(injectable_light_curve)
        injectable_light_curve_figure = figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
        injectable_light_curve_figure.scatter(x=injectable_light_curve.times, y=injectable_light_curve.fluxes)
        injectable_light_curve_figure.line(x=injectable_light_curve.times, y=injectable_light_curve.fluxes, line_alpha=0.3)

        injectee_light_curve_path = Path(
            'data/spoc_transit_experiment/train/negatives/hlsp_tess-spoc_tess_phot_0000000000054423-s0038_tess_v1_lc.fits')
        injectee_light_curve = TessMissionLightCurve.from_path(injectee_light_curve_path)
        injectee_light_curve = LightCurve.new(times=injectee_light_curve.times, fluxes=injectee_light_curve.fluxes)
        injectee_light_curve = remove_nan_flux_data_points_from_light_curve(injectee_light_curve)
        injectee_light_curve_figure = figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
        injectee_light_curve_figure.scatter(x=injectee_light_curve.times, y=injectee_light_curve.fluxes)
        injectee_light_curve_figure.line(x=injectee_light_curve.times, y=injectee_light_curve.fluxes, line_alpha=0.3)

        injectable_light_curve_observation = LightCurveObservation.new(injectable_light_curve, label=1)
        injectee_light_curve_observation = LightCurveObservation.new(injectee_light_curve, label=0)
        injected_light_curve_observation = inject_light_curve(injectee_light_curve_observation,
                                                              injectable_light_curve_observation)
        injected_light_curve = injected_light_curve_observation.light_curve
        #print(injected_light_curve.times[0])

        injected_light_curve_figure = figure(x_axis_label='Time (BTJD)', y_axis_label='Flux')
        injected_light_curve_figure.scatter(x=injected_light_curve.times, y=injected_light_curve.fluxes)
        injected_light_curve_figure.line(x=injected_light_curve.times, y=injected_light_curve.fluxes, line_alpha=0.3)
        #2353.34, 2360.24

        period = 6.9
        times = injected_light_curve.times
        fluxes = injected_light_curve.fluxes
        times = np.array(times)
        fluxes = np.array(fluxes)
        lk_light_curve = lk.LightCurve(time=times, flux=fluxes)
        periodogram = BoxLeastSquaresPeriodogram.from_lightcurve(lk_light_curve)
        #periodogram = LombScarglePeriodogram.from_lightcurve(lk_light_curve)
        best_period2 = periodogram.period_at_max_power.value

        period = periodogram.period
        power = periodogram.power
        power_spectrum_figure = figure()
        power_spectrum_figure.line(x=period, y=power)
        show(power_spectrum_figure)
        print("Best period2:", best_period2)

        minimum_period__days = (20 * units.min).to(units.d).value
        maximum_period__days = (27 * units.d).value
        maximum_frequency__per_day = 1 / minimum_period__days
        minimum_frequency__per_day = 1 / maximum_period__days
        frequency, power = LombScargle(times, fluxes).autopower(minimum_frequency=minimum_frequency__per_day, maximum_frequency=maximum_frequency__per_day, samples_per_peak=50)
        best_frequency = frequency[np.argmax(power)]
        period = 1 / frequency
        power_spectrum_figure = figure()
        power_spectrum_figure.line(x=period, y=power)
        #show(power_spectrum_figure)
        best_period = 1. / best_frequency
        phases = (times % best_period2) / best_period2
        folded_light_curve_figure = figure(x_axis_label='Phase', y_axis_label='Flux')
        folded_light_curve_figure.scatter(x=phases, y=fluxes)
        folded_light_curve_figure.line(x=phases, y=fluxes, line_alpha=0.3)

        show(folded_light_curve_figure)

        #column = Column(injectable_light_curve_figure, injectee_light_curve_figure, injected_light_curve_figure)
        #show(column)
        #save(column, 'injection_figure.html')

        combined_figure = figure(x_axis_label='Time', y_axis_label='Flux')
        combined_figure.scatter(x=injectee_light_curve.times, y=injectee_light_curve.fluxes, legend_label='Injectee', color='blue')
        combined_figure.line(x=injectee_light_curve.times, y=injectee_light_curve.fluxes, line_alpha=0.3, color='blue')
        combined_figure.scatter(x=injected_light_curve.times, y=injected_light_curve.fluxes, legend_label='Injected', color='orange')
        combined_figure.line(x=injected_light_curve.times, y=injected_light_curve.fluxes, line_alpha=0.3, color='orange')
        show(combined_figure)
        save(combined_figure, 'combined.html')
        # all_combined_figures.append(combined_figure)
    #
    # layout = column(*all_combined_figures)
    # show(layout)
    # save(layout, 'all_combined_figures.html')


if __name__ == '__main__':
    plottingTheTopConfidences()
    #main()