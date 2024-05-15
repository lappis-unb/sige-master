import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from apps.utils.helpers import log_service

logger = logging.getLogger("apps")


class LTTBDownSampler:
    """A service class for downsampling time series data using the LTTB algorithm,
    supporting combined and reference-based indexing."""

    def __init__(self, n_out, enable_parallel=False):
        if n_out <= 2:
            raise ValueError("n_out should be greater than 2.")

        self.n_out = n_out
        self.enable_parallel = enable_parallel

    @log_service()
    def apply_lttb(self, data, dt_column="collection_date", ref_column=None):
        if self.n_out > data.shape[0]:
            return data

        try:
            self.valid_dataframe(data, dt_column, ref_column)
        except ValueError as e:
            logger.warning(f"Invalid DataFrame: {e}")
            return data

        df_prepared = self._prepare_dataframe(data, dt_column)
        indices = self._downsample_dataframe(df_prepared, ref_column)
        return data.loc[indices]

    def _prepare_dataframe(self, data, dt_column):
        df = data.copy()
        if dt_column not in df.columns:
            raise ValueError(f"Column '{dt_column}' not found in the DataFrame.")

        df = df.rename(columns={dt_column: "x"})
        df["x"] = pd.to_datetime(df["x"]).apply(lambda x: x.timestamp())
        return df

    def _downsample_dataframe(self, df, ref_column):
        if ref_column and ref_column not in df.columns:
            raise ValueError(f"Column '{ref_column}' not found in DataFrame.")

        if ref_column is None:
            indices = self._downsample_all_columns(df)
            return list(np.unique(indices))
        elif self.enable_parallel:
            return self._downsample_parallel(df)
        else:
            downsample_df = df[["x", ref_column]].rename(columns={ref_column: "y"})
            return self._downsample_column(downsample_df)

    def _parallel_downsample(self, df):
        indices = []

        num_workers = min(len(df.columns), 8)
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for column in df.columns[1:]:
                df_downsample = df[["x", column]].rename(columns={column: "y"})
                futures.append(executor.submit(self._downsample_column, df_downsample))

            for future in as_completed(futures):
                indices.extend(future.result())
        return np.unique(indices)

    def _downsample_all_columns(self, df):
        indices_columns = []
        for column in df.columns[1:]:
            df_downsample = df[["x", column]].rename(columns={column: "y"})
            indices = self._downsample_column(df_downsample)
            indices_columns.extend(indices)
        return np.unique(indices_columns)

    def _downsample_column(self, df):
        if df["y"].dtype != float:
            df["y"] = df["y"].astype(float, errors="ignore")

        data = df[["x", "y"]].to_numpy()
        return self._lttb_core(data)

    def _lttb_core(self, data):
        n_bins = self.n_out - 2
        data_bins = np.array_split(data[1:-1], n_bins)
        indices = np.zeros(self.n_out, dtype=int)  # Array to store indices
        indices[0], indices[-1] = 0, len(data) - 1
        start_indices = self._calculate_start_indices(data_bins)

        for i in range(n_bins):
            a = data[indices[i]]
            bs = data_bins[i]
            next_bin = data_bins[i + 1] if i < n_bins - 1 else data[-1:]
            c = next_bin.mean(axis=0)
            areas = self._areas_of_triangles(a, bs, c)
            max_index = np.argmax(areas)
            indices[i + 1] = start_indices[i] + max_index
        return indices

    def _areas_of_triangles(self, a, bs, c):
        a_to_c = c - a
        return 0.5 * np.abs(a_to_c[0] * (bs[:, 1] - a[1]) - a_to_c[1] * (bs[:, 0] - a[0]))

    def _calculate_start_indices(self, data_bins):
        start_indices = [1]
        for i in range(1, len(data_bins)):
            start_indices.append(start_indices[-1] + len(data_bins[i - 1]))
        return start_indices

    def valid_dataframe(self, df, dt_column, ref_column):
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input data should be a pandas DataFrame.")

        if df.columns[0] != dt_column:
            raise ValueError(f"Column '{df.columns[0]}' should not be '{dt_column}'")

        if len(df.columns) < 2:
            raise ValueError("Dataframe should have at least 2 columns.")
