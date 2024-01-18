# -*- coding: utf-8 -*-

import glob
import os

import click
import pandas as pd


@click.command()
@click.argument('input_path')
@click.argument('filename')
def make_dataframe(input_path: str, filename: str):
    input_files = glob.glob(os.path.join(input_path, '*.zip'))
    dfs = []
    for input_file in input_files:
        dfs.append(pd.read_csv(input_file, encoding='cp932', index_col=0))

    df = pd.concat(dfs, ignore_index=True)
    df.to_csv(filename)


if __name__ == '__main__':
    make_dataframe()
