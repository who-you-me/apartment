# -*- coding: utf-8 -*-

import csv
import json

import click
import numpy as np


@click.command()
@click.argument('input_path')
@click.argument('output_path')
def geo(input_path: str, output_path: str):
    with open(input_path) as f:
        data = json.load(f)

    rows = []
    for row in data['features']:
        properties = row['properties']
        company = properties['N02_004']
        line = properties['N02_003']
        station = properties['N02_005']

        geometry = row['geometry']
        coordinates = np.array(geometry['coordinates'][0]).mean(axis=0)
        rows.append([station, line, company, coordinates[1], coordinates[0]])

    with open(output_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['station', 'company', 'line', 'lat', 'lng'])
        writer.writerows(rows)


if __name__ == '__main__':
    geo()
