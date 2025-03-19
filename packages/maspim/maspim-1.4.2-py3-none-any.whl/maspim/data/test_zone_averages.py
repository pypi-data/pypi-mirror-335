import pandas as pd
import numpy as np

from tqdm import tqdm

from maspim.data.main import Data

np.random.seed(0)


def get_example():
    # construct example
    n_rows = 5
    n_cols = 10

    data = np.array([0, 4, np.nan, 4, 4])[:, np.newaxis] * np.ones(n_cols)[np.newaxis, :]

    df = pd.DataFrame(data=data)
    zones_column = np.zeros(n_rows)
    df.loc[:, zones_key] = zones_column
    df.loc[:, 'x'] = np.nan
    return df


def new(zones_key, columns):
    zones_column = data_table.loc[:, zones_key]
    zones: np.ndarray = np.unique(zones_column)

    averages: np.ndarray = np.empty((len(zones), data_table.shape[1]))
    stds: np.ndarray = np.empty((len(zones), data_table.shape[1]))
    Ns: np.ndarray = np.empty((len(zones), data_table.shape[1]))

    # iterate over zones
    for idx, zone in tqdm(
            enumerate(zones),
            total=len(zones),
            desc='averaging values for zones'
    ):
        # average of each component in that zone
        # pixel mask: where entry in zones_key matches key
        mask_pixels_in_zone: np.ndarray[bool] = zones_column == zone
        # sub dataframe of data_table only containing pixels in zone
        pixels_in_zone: pd.DataFrame = data_table.loc[mask_pixels_in_zone, :]
        # pd.Series, averages for each compound in that zone
        averages[idx, :] = pixels_in_zone.mean(axis=0, skipna=True)

        # sigma = sqrt(1/(N - 1) * sum(x_i - mu))
        stds[idx, :] = pixels_in_zone.std(axis=0, skipna=True, ddof=1)
        Ns[idx, :] = (pixels_in_zone > 0).sum(axis=0, skipna=True)


zones_key = 'zone'
data_table = get_example()

data = Data()
data._feature_table = data_table
avs_f, stds_f, ns_f = data.processing_zone_wise_average(zones_key=zones_key, calc_std=True, exclude_zeros=True)


