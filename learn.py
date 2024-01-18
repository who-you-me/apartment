# -*- coding: utf-8 -*-

import pickle
import re
from typing import Any, List, Optional, Tuple

import click
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def to_ad(value: str) -> Optional[int]:
    m = re.match(r'(昭和|平成|令和)(\d{1,2}|元)年', value)
    if not m:
        return None
    era = m.group(1)
    year = 1 if m.group(2) == '元' else int(m.group(2))

    if era == '昭和':
        return 1925 + year
    elif era == '平成':
        return 1988 + year
    elif era == '令和':
        return 2018 + year


def to_year(value: str) -> Optional[int]:
    year = value[:4]
    if year.isdigit():
        return int(year)


def to_distance(value: str) -> Optional[float]:
    if value.isdigit():
        return int(value)


def to_index(row: pd.Series) -> Tuple[pd.Series, List[Any]]:
    values = {v: i + 1 for i, v in enumerate(sorted(row.unique()))}
    return row.map(values), list(values.keys())


@click.command()
@click.argument('input_path')
@click.argument('output_path')
def feature_engineering(input_path: str, output_path: str):
    df = pd.read_csv(input_path, index_col=0)
    df = df[df['種類'] == '中古マンション等'].copy()

    needed_columns = ['最寄駅：名称', '最寄駅：距離（分）', '取引価格（総額）', '面積（㎡）', '建築年', '取引時点', '改装']
    df = df.replace({'2000㎡以上': np.nan})
    df['改装'].fillna('未改装', inplace=True)
    df = df.dropna(axis=0, subset=needed_columns)

    df['price'] = df['取引価格（総額）'] / df['面積（㎡）'].astype(float)
    df['bought_at'] = df['取引時点'].apply(to_year)
    df['built_at'] = df['建築年'].apply(to_ad)
    df['age'] = df['bought_at'] - df['built_at']
    df['station'] = df['最寄駅：名称']
    df['station'], stations = to_index(df['最寄駅：名称'])
    df['distance'] = df['最寄駅：距離（分）'].apply(to_distance)
    df['reform'] = (df['改装'] == '改装済').astype(int)

    used_columns = ['price', 'bought_at', 'station', 'distance', 'age', 'reform']
    fe_df = df[used_columns].dropna(axis=0).copy()

    model = smf.ols(formula='price ~ C(bought_at) + C(station) + distance + age + reform', data=fe_df)
    fit_result = model.fit()

    with open(output_path, 'wb') as f:
        result = {'df': fe_df, 'model': model, 'fit_result': fit_result, 'stations': stations}
        pickle.dump(result, f)


if __name__ == '__main__':
    feature_engineering()
