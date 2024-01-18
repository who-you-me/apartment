# -*- coding: utf-8 -*-

import csv
import pickle

import folium
import click
from matplotlib import cm
from matplotlib.colors import rgb2hex


@click.command()
@click.argument('result_path')
@click.argument('geo_path')
@click.argument('output_path')
def output(result_path: str, geo_path: str, output_path: str):
    with open(result_path, 'rb') as f:
        result = pickle.load(f)

    with open(geo_path) as f:
        reader = csv.reader(f)
        next(reader)
        geo = {row[0]: [float(row[1]), float(row[2])] for row in reader}

    params = dict(result['fit_result'].params)
    intercept = params['Intercept']
    coef_2021 = params['C(bought_at)[T.2021]']

    station_intercepts = {}
    for i, station in enumerate(result['stations']):
        key = f'C(station)[T.{i + 1}]'
        if i == 0:
            station_intercepts[station] = intercept + coef_2021
        elif key in params:
            station_intercepts[station] = intercept + coef_2021 + params[key]
        else:
            print(i, station)
            station_intercepts[station] = None

    color_map = cm.get_cmap('Reds')
    df = result['df']
    counts = dict(df[df['bought_at'] >= 2019].groupby('station')['station'].count())
    min_c = 0
    max_c = max(counts.values())

    figure = folium.Figure(width=1000, height=500)
    # m = folium.Map([43.06008, 141.35225], zoom_start=12).add_to(figure)
    m = folium.Map([35.68110333333333, 139.76788], zoom_start=12).add_to(figure)

    min_v = min(v for v in station_intercepts.values() if v)
    max_v = max(v for v in station_intercepts.values() if v)
    for i, (station, value) in enumerate(station_intercepts.items()):
        if not value:
            continue

        n = counts.get(i + 1, 0)
        radius = 5 + 25 * ((n - min_c) / (max_c - min_c))
        color = int(10 + 245 * (value - min_v) / (max_v - min_v))
        folium.CircleMarker(
            location=geo[station],
            radius=radius,
            popup=folium.map.Popup(f'{station}<br />{n}<br />{int(value):,}円/㎡', max_width='150'),
            fill=True,
            color=rgb2hex(color_map(color))
        ).add_to(m)

    figure.save(outfile=output_path)

    for k, v in params.items():
        print(f'{k}\t{int(v):,}')


if __name__ == '__main__':
    output()
