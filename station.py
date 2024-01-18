# -*- coding: utf-8 -*-

import csv
import pickle
import unicodedata

import click


@click.command()
@click.argument('result_path')
@click.argument('geo_path')
@click.argument('output_path')
def station(result_path: str, geo_path: str, output_path: str):
    with open(result_path, 'rb') as f:
        result = pickle.load(f)

    with open(geo_path) as f:
        reader = csv.reader(f)
        geo = [row for row in reader]

    rows = []
    for value in result['stations']:
        normalized = unicodedata.normalize('NFKC', value)
        if '(' in normalized:
            rows.append([value, None, None])
        else:
            for row in geo:
                if normalized == row[0]:
                    rows.append([value, row[3], row[4]])
                    break
            else:
                rows.append([value, None, None])

    with open(output_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['station', 'lat', 'lng'])
        writer.writerows(rows)


if __name__ == '__main__':
    station()
