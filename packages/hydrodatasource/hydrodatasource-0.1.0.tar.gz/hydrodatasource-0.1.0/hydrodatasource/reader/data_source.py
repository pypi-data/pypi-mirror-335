import collections
import glob
import json
import os
import re
import numpy as np
import pandas as pd
import xarray as xr
from abc import ABC
from tqdm import tqdm
import polars as pl

from hydroutils import hydro_file
from hydroutils.hydro_time import generate_start0101_time_range

import hydrodatasource.configs.config as conf
from hydrodatasource.configs.config import CACHE_DIR
from hydrodatasource.configs.data_consts import (
    ERA5LAND_ET_REALATED_VARS,
    MODIS_ET_PET_8D_VARS,
)
from hydrodatasource.utils.utils import (
    cal_area_from_shp,
    calculate_basin_offsets,
    is_minio_folder,
    minio_file_list,
)
from hydrodatasource.reader import access_fs
import geopandas as gpd


class HydroData(ABC):
    """An interface for reading multi-modal data sources.

    Parameters
    ----------
    ABC : _type_
        _description_
    """

    def __init__(self, data_path):
        self.data_source_dir = data_path

    def get_name(self):
        raise NotImplementedError

    def set_data_source_describe(self):
        raise NotImplementedError

    def read_data(self):
        raise NotImplementedError


class SelfMadeHydroDataset(HydroData):
    """A class for reading hydrodataset, but not really ready-datasets,
    just some data directorys organized like a HydroDataset.

    NOTE:
    We compile forcing data and attr data into a directory,
    organized like a ready dataset -- like Caravan.
    Only two directories are needed: attributes and timeseries
    """

    def __init__(
        self, data_path, download=False, time_unit=None, dataset_name=None, **kwargs
    ):
        """Initialize a self-made Caravan-style dataset.

        Parameters
        ----------
        data_path : _type_
            _description_
        download : bool, optional
            _description_, by default False
        time_unit : list, optional
            we have different time units, by default None
        dataset_name : _type_, optional
            SelfMadeHydroDataset's name, different dataset may use this same datasource class, by default None
        """
        if time_unit is None:
            time_unit = ["1D"]
        if any(unit not in ["1h", "3h", "1D", "8D"] for unit in time_unit):
            raise ValueError(
                "time_unit must be one of ['1h', '3h', '1D', '8D']. We only support these time units now."
            )
        # TODO: maybe starting with "s3://" is a better idea?
        self.head = "minio" if "s3://" in data_path else "local"
        super().__init__(data_path)
        self.data_source_description = self.set_data_source_describe()
        if download:
            self.download_data_source()
        self.camels_sites = self.read_site_info()
        self.time_unit = time_unit
        self.dataset_name = dataset_name
        self.version = kwargs.get("version", None)

    @property
    def streamflow_unit(self):
        unit_mapping = {"1h": "mm/h", "3h": "mm/3h", "1D": "mm/d"}
        return {unit: unit_mapping[unit] for unit in self.time_unit}

    def get_name(self):
        return "SelfMadeHydroDataset"

    def set_data_source_describe(self):
        data_root_dir = self.data_source_dir
        ts_dir = os.path.join(data_root_dir, "timeseries")
        # we assume that each subdirectory in ts_dir represents a time unit
        # In this subdirectory, there are csv files for each basin
        if "s3://" in data_root_dir:
            time_units_dir = [
                os.path.join(ts_dir, name)
                for name in minio_file_list(ts_dir)
                if is_minio_folder(os.path.join(ts_dir, name))
            ]
        else:
            time_units_dir = [
                os.path.join(ts_dir, name)
                for name in os.listdir(ts_dir)
                if os.path.isdir(os.path.join(ts_dir, name))
            ]
        pattern = os.path.join(ts_dir, "*_units_info.json")
        unit_files = glob.glob(pattern)
        attr_dir = os.path.join(data_root_dir, "attributes")
        attr_file = os.path.join(attr_dir, "attributes.csv")
        shape_dir = os.path.join(data_root_dir, "shapes")

        return collections.OrderedDict(
            DATA_DIR=data_root_dir,
            TS_DIRS=time_units_dir,
            ATTR_DIR=attr_dir,
            ATTR_FILE=attr_file,
            UNIT_FILES=unit_files,
            SHAPE_DIR=shape_dir,
        )

    def download_data_source(self):
        print(
            "Please download it manually and put all files of a CAMELS dataset in the CAMELS_DIR directory."
        )
        print("We unzip all files now.")

    def read_site_info(self):
        camels_file = self.data_source_description["ATTR_FILE"]
        attrs = access_fs.spec_path(camels_file, head=self.head)
        return attrs[["basin_id", "area"]]

    def read_object_ids(self, object_params=None) -> np.array:
        return self.camels_sites["basin_id"].values

    def read_timeseries(
        self, object_ids=None, t_range_list: list = None, relevant_cols=None, **kwargs
    ) -> dict:
        """
        Returns a dictionary containing data with different time scales.

        Parameters
        ----------
        object_ids : list, optional
            List of object IDs. Defaults to None.
        t_range_list : list, optional
            List of time ranges. Defaults to None.
        relevant_cols : list, optional
            List of relevant columns. Defaults to None.
        **kwargs : dict, optional
            Additional keyword arguments.

        Returns
        -------
        dict
            A dictionary containing data with different time scales.
        """
        time_units = kwargs.get("time_units", ["1D"])
        start0101_freq = kwargs.get("start0101_freq", False)

        results = {}

        for time_unit in time_units:
            # whether to convert the time to UTC, for 1D time unit, default set False,
            # and for 3h time unit, set True
            offset_to_utc = time_unit == "3h"
            if offset_to_utc:
                basinoutlets_path = os.path.join(
                    self.data_source_description["SHAPE_DIR"], "basinoutlets.shp"
                )
                try:
                    offset_dict = calculate_basin_offsets(basinoutlets_path)
                except:
                    raise FileNotFoundError(
                        f"basinoutlets.shp not found in {basinoutlets_path}."
                    )
            ts_dir = self._get_ts_dir(
                self.data_source_description["TS_DIRS"], time_unit
            )
            if start0101_freq:
                t_range = generate_start0101_time_range(
                    start_time=t_range_list[0],
                    end_time=t_range_list[-1],
                    freq=time_unit,
                )
            else:
                t_range = pd.date_range(
                    start=t_range_list[0], end=t_range_list[-1], freq=time_unit
                )
            nt = len(t_range)
            x = np.full([len(object_ids), nt, len(relevant_cols)], np.nan)

            for k in tqdm(
                range(len(object_ids)), desc=f"Reading timeseries data with {time_unit}"
            ):
                ts_file = os.path.join(
                    ts_dir,
                    object_ids[k] + ".csv",
                )
                if "s3://" in ts_file:
                    with conf.FS.open(ts_file, mode="rb") as f:
                        ts_data = pd.read_csv(f, engine="c")
                else:
                    ts_data = pd.read_csv(ts_file, engine="c")
                date = pd.to_datetime(ts_data["time"]).values
                if offset_to_utc:
                    date = date - np.timedelta64(offset_dict[object_ids[k]], "h")
                [_, ind1, ind2] = np.intersect1d(date, t_range, return_indices=True)

                for j in range(len(relevant_cols)):
                    tmp_ = self._read_timeseries_1basin1var(ts_data, relevant_cols[j])
                    x[k, ind2, j] = tmp_[ind1]

            results[time_unit] = x

        return results

    def _read_timeseries_1basin1var(self, ts_data, relevant_col):
        if "precipitation" in relevant_col:
            prcp = ts_data[relevant_col].values
            prcp[prcp < 0] = 0.0
            return prcp
        elif relevant_col in ERA5LAND_ET_REALATED_VARS:
            evap = -1 * ts_data[relevant_col].values
            evap[evap < 0] = 0.0
            return evap
        elif relevant_col in MODIS_ET_PET_8D_VARS:
            modis_values = ts_data[relevant_col].values
            modis_dates = pd.to_datetime(ts_data["time"].values)
            for idx, current_date in enumerate(modis_dates):
                # Check if the date is prior to or on January 1st
                if current_date.month == 1 and current_date.day == 1:
                    if idx == 0:
                        # First day is January 1st, no previous date to scale from
                        continue
                        # Get the previous date
                    previous_date = modis_dates[idx - 1]
                    # Calculate the number of days between the previous date and January 1st
                    delta_days = (current_date - previous_date).days

                    # Adjust the MODIS value based on the number of days between the previous date and January 1st
                    if delta_days > 0:
                        modis_values[idx - 1] = modis_values[idx - 1] * 8 / delta_days
            # NOTE: MODIS ET values are ACTUALLY in 0.1mm/day, so we need to convert to mm/day
            return modis_values * 0.1
        else:
            return ts_data[relevant_col].values

    def read_attributes(
        self, object_ids=None, constant_cols=None, **kwargs
    ) -> np.array:
        """2d data (site_num * var_num), non-time-series data"""
        attr_file = self.data_source_description["ATTR_FILE"]
        if "s3://" in attr_file:
            with conf.FS.open(attr_file, mode="rb") as f:
                attrs = pd.read_csv(f, dtype={"basin_id": str})
        else:
            attrs = pd.read_csv(attr_file, dtype={"basin_id": str})
        if object_ids is None:
            if constant_cols is None:
                return attrs
            object_ids = attrs["basin_id"].values
        if constant_cols is None:
            constant_cols = attrs.columns.values
        x = np.full([len(object_ids), len(constant_cols)], np.nan)
        for k in range(len(object_ids)):
            ind = attrs["basin_id"] == object_ids[k]
            for j in range(len(constant_cols)):
                x[k, j] = attrs[constant_cols[j]][ind].values
        return x

    def get_attributes_cols(self) -> np.array:
        """the constant cols in this data_source"""
        attr_file = self.data_source_description["ATTR_FILE"]
        if "s3://" in attr_file:
            with conf.FS.open(attr_file, mode="rb") as f:
                attrs = pd.read_csv(f, dtype={"basin_id": str})
        else:
            attrs = pd.read_csv(attr_file, dtype={"basin_id": str})
        attr_units = attrs.columns.values
        return self._check_vars_in_unitsinfo(attr_units)

    def get_timeseries_cols(self) -> np.array:
        """the relevant cols in this data_source"""
        ts_dirs = self.data_source_description["TS_DIRS"]
        unit_files = self.data_source_description["UNIT_FILES"]
        all_vars = {}
        for time_unit in self.time_unit:
            # Find the directory that corresponds to the current time unit
            ts_dir = self._get_ts_dir(ts_dirs, time_unit)
            # Find the corresponding unit file
            unit_file = next(
                file
                for file in unit_files
                if f"{time_unit}_units_info.json" == file.split(os.sep)[-1]
            )
            # Load the first CSV file in the directory to extract column names
            if "s3://" in ts_dir:
                ts_file = os.path.join(ts_dir, minio_file_list(ts_dir)[0])
                with conf.FS.open(ts_file, mode="rb") as f:
                    ts_tmp = pd.read_csv(f, dtype={"basin_id": str})
            else:
                ts_file = os.path.join(ts_dir, os.listdir(ts_dir)[0])
                ts_tmp = pd.read_csv(ts_file, dtype={"basin_id": str})
            # Get the relevant forcing units and validate against unit info
            forcing_units = ts_tmp.columns.values[1:]
            the_vars = self._check_vars_in_unitsinfo(forcing_units, unit_file)
            # Map the variables to the corresponding time unit
            all_vars[time_unit] = the_vars
        return all_vars

    def _get_ts_dir(self, ts_dirs, time_unit):
        """we add version for ts directory, so we need to find the correct ts directory

        Parameters
        ----------
        ts_dirs : list
            the list of ts directories without version
        time_unit : str
            the time unit

        Returns
        -------
        _type_
            _description_
        """
        ts_dir = next(
            dir_path for dir_path in ts_dirs if time_unit == dir_path.split(os.sep)[-1]
        )
        version = self.version
        ts_dir = (
            ts_dir + f"_{version}" if version is not None and version != "" else ts_dir
        )

        return ts_dir

    def _check_vars_in_unitsinfo(self, vars, unit_file=None):
        """If a var is not recorded in a units_info file, we will not use it.

        Parameters
        ----------
        vars : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        if unit_file is None:
            # For attributes, all the variables' units are same in all unit_info files
            # hence, we just chose the first one
            unit_file = self.data_source_description["UNIT_FILES"][0]
        if "s3://" in unit_file:
            with conf.FS.open(unit_file, mode="rb") as fp:
                units_info = json.load(fp)
        else:
            units_info = hydro_file.unserialize_json(unit_file)
        vars_final = [var_ for var_ in vars if var_ in units_info]
        return np.array(vars_final)

    def cache_attributes_xrdataset(self):
        """Convert all the attributes to a single dataset

        Returns
        -------
        None
        """
        # NOTICE: although it seems that we don't use pint_xarray, we have to import this package
        import pint_xarray  # noqa: F401

        shape_dir = os.path.join(
            self.data_source_description["SHAPE_DIR"], "basins.shp"
        )
        if "s3://" in shape_dir:
            with conf.FS.open(shape_dir, mode="rb") as f:
                shape = gpd.read_file(f)
        else:
            shape = gpd.read_file(shape_dir)
        df_area = cal_area_from_shp(shape)  # calculate the area from shape file
        df_area.set_index("basin_id", inplace=True)

        df_attr = self.read_attributes()
        df_attr.set_index("basin_id", inplace=True)
        df_attr = df_attr.join(df_area)
        # Mapping provided units to the variables in the datasets
        # For attributes, all the variables' units are same in all unit_info files
        # hence, we just chose the first one
        if "s3://" in self.data_source_description["UNIT_FILES"][0]:
            with conf.FS.open(
                self.data_source_description["UNIT_FILES"][0], mode="rb"
            ) as fp:
                units_dict = json.load(fp)
        else:
            units_dict = hydro_file.unserialize_json(
                self.data_source_description["UNIT_FILES"][0]
            )
        units_dict["shp_area"] = "km^2"  # add the unit of shp_area
        # Convert string columns to categorical variables and record categorical mappings
        categorical_mappings = {}
        for column in df_attr.columns:
            if df_attr[column].dtype == "object":
                df_attr[column] = df_attr[column].astype("category")
                categorical_mappings[column] = dict(
                    enumerate(df_attr[column].cat.categories)
                )
                df_attr[column] = df_attr[column].cat.codes

        ds = xr.Dataset()
        for column in df_attr.columns:
            attrs = {"units": units_dict.get(column, "unknown")}
            if column in categorical_mappings:
                attrs["category_mapping"] = categorical_mappings[column]

            data_array = xr.DataArray(
                data=df_attr[column].values,
                dims=["basin"],
                # we have set gage_id as index so that it won't be saved as numeric values
                coords={"basin": df_attr.index.values.astype(str)},
                attrs=attrs,
            )
            ds[column] = data_array

        # Convert categorical mappings to strings
        for column in ds.data_vars:
            if "category_mapping" in ds[column].attrs:
                # Convert the dictionary to a string
                mapping_str = str(ds[column].attrs["category_mapping"])
                ds[column].attrs["category_mapping"] = mapping_str
        dataset_name = self.dataset_name
        prefix_ = "" if dataset_name is None else dataset_name + "_"
        ds.to_netcdf(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))

    def cache_timeseries_xrdataset(self, t_range=None, **kwargs):
        """Save all timeseries data in separate NetCDF files for each time unit.

        Parameters
        ----------
        t_range : list, optional
            Time range for the data, by default ["1980-01-01", "2023-12-31"]
        kwargs : dict, optional
            batchsize -- Number of basins to process per batch, by default 100
            time_units -- List of time units to process, by default None
            start0101_freq -- for freq setting, if the start date is 01-01, set True, by default False
        """
        batchsize = kwargs.get("batchsize", 100)
        time_units = kwargs.get("time_units", self.time_unit) or [
            "1D"
        ]  # Default to ["1D"] if not specified or if time_units is None
        start0101_freq = kwargs.get("start0101_freq", False)

        variables = self.get_timeseries_cols()
        basins = self.camels_sites["basin_id"].values

        # Define the generator function for batching
        def data_generator(basins, batch_size):
            for i in range(0, len(basins), batch_size):
                yield basins[i : i + batch_size]

        for time_unit in time_units:
            if t_range is None:
                if time_unit != "3h":
                    t_range = ["1980-01-01", "2023-12-31"]
                else:
                    t_range = ["1980-01-01 01", "2023-12-31 22"]

            # Generate the time range specific to the time unit
            if start0101_freq:
                times = (
                    generate_start0101_time_range(
                        start_time=t_range[0], end_time=t_range[-1], freq=time_unit
                    )
                    .strftime("%Y-%m-%d %H:%M:%S")
                    .tolist()
                )
            else:
                times = (
                    pd.date_range(start=t_range[0], end=t_range[-1], freq=time_unit)
                    .strftime("%Y-%m-%d %H:%M:%S")
                    .tolist()
                )
            # Retrieve the correct units information for this time unit
            unit_file = next(
                file
                for file in self.data_source_description["UNIT_FILES"]
                if time_unit in file
            )
            if "s3://" in unit_file:
                with conf.FS.open(unit_file, mode="rb") as fp:
                    units_info = json.load(fp)
            else:
                units_info = hydro_file.unserialize_json(unit_file)

            for basin_batch in data_generator(basins, batchsize):
                data = self.read_timeseries(
                    object_ids=basin_batch,
                    t_range_list=t_range,
                    relevant_cols=variables[
                        time_unit
                    ],  # Ensure we use the right columns for the time unit
                    time_units=[
                        time_unit
                    ],  # Pass the time unit to ensure correct data retrieval
                    start0101_freq=start0101_freq,
                )

                dataset = xr.Dataset(
                    data_vars={
                        variables[time_unit][i]: (
                            ["basin", "time"],
                            data[time_unit][:, :, i],
                            {"units": units_info[variables[time_unit][i]]},
                        )
                        for i in range(len(variables[time_unit]))
                    },
                    coords={
                        "basin": basin_batch,
                        "time": pd.to_datetime(times),
                    },
                )

                # Save the dataset to a NetCDF file for the current batch and time unit
                prefix_ = self._get_ts_file_prefix_(self.dataset_name, self.version)
                batch_file_path = os.path.join(
                    CACHE_DIR,
                    f"{prefix_}timeseries_{time_unit}_batch_{basin_batch[0]}_{basin_batch[-1]}.nc",
                )
                dataset.to_netcdf(batch_file_path)

                # Release memory by deleting the dataset
                del dataset
                del data

    def cache_xrdataset(self, t_range=None, time_units=None):
        """Save all data in a netcdf file in the cache directory"""
        self.cache_attributes_xrdataset()
        self.cache_timeseries_xrdataset(t_range=t_range, time_units=time_units)

    def read_ts_xrdataset(
        self,
        gage_id_lst: list = None,
        t_range: list = None,
        var_lst: list = None,
        **kwargs,
    ) -> dict:
        """
        Read time-series xarray dataset from multiple NetCDF files and organize them by time units.

        Parameters:
        ----------
        gage_id_lst: list - List of gage IDs to select.
        t_range: list - List of two elements [start_time, end_time] to select time range.
        var_lst: list - List of variables to select.
        **kwargs: Additional arguments.

        Returns:
        ----------
        dict: A dictionary where each key is a time unit and each value is an xarray.Dataset containing the selected gage IDs, time range, and variables.
        """
        dataset_name = self.dataset_name
        version = self.version
        time_units = kwargs.get("time_units", self.time_unit)
        if var_lst is None:
            return None

        # Initialize a dictionary to hold datasets for each time unit
        datasets_by_time_unit = {}

        prefix_ = self._get_ts_file_prefix_(dataset_name, version)

        for time_unit in time_units:
            # Collect batch files specific to the current time unit
            batch_files = [
                os.path.join(CACHE_DIR, f)
                for f in os.listdir(CACHE_DIR)
                if re.match(
                    rf"^{prefix_}timeseries_{time_unit}_batch_[A-Za-z0-9_]+_[A-Za-z0-9_]+\.nc$",
                    f,
                )
            ]

            if not batch_files:
                # Cache the data if no batch files are found for the current time unit
                self.cache_timeseries_xrdataset(**kwargs)
                batch_files = [
                    os.path.join(CACHE_DIR, f)
                    for f in os.listdir(CACHE_DIR)
                    if re.match(
                        rf"^{prefix_}timeseries_{time_unit}_batch_[A-Za-z0-9_]+_[A-Za-z0-9_]+\.nc$",
                        f,
                    )
                ]

            selected_datasets = []

            for batch_file in batch_files:
                ds = xr.open_dataset(batch_file)
                all_vars = ds.data_vars
                if any(var not in ds.variables for var in var_lst):
                    raise ValueError(f"var_lst must all be in {all_vars}")
                if valid_gage_ids := [
                    gid for gid in gage_id_lst if gid in ds["basin"].values
                ]:
                    ds_selected = ds[var_lst].sel(
                        basin=valid_gage_ids, time=slice(t_range[0], t_range[1])
                    )
                    selected_datasets.append(ds_selected)

                ds.close()  # Close the dataset to free memory

            # If any datasets were selected, concatenate them along the 'basin' dimension
            if selected_datasets:
                # NOTE: the chosen part must be sorted by basin, or there will be some negative sideeffect for continue usage of this repo
                datasets_by_time_unit[time_unit] = xr.concat(
                    selected_datasets, dim="basin"
                ).sortby("basin")
            else:
                datasets_by_time_unit[time_unit] = xr.Dataset()

        return datasets_by_time_unit

    def _get_ts_file_prefix_(self, dataset_name, version):
        prefix_ = "" if dataset_name is None else dataset_name + "_"
        # we add version for prefix_ as we will update the dataset iteratively
        prefix_ = prefix_ + f"{version}_" if version is not None else prefix_
        return prefix_

    def read_attr_xrdataset(self, gage_id_lst=None, var_lst=None, **kwargs):
        dataset_name = self.dataset_name

        prefix_ = "" if dataset_name is None else dataset_name + "_"
        if var_lst is None or len(var_lst) == 0:
            return None
        try:
            attr = xr.open_dataset(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))
        except FileNotFoundError:
            self.cache_attributes_xrdataset()
            attr = xr.open_dataset(os.path.join(CACHE_DIR, f"{prefix_}attributes.nc"))
        return attr[var_lst].sel(basin=gage_id_lst)

    def read_area(self, gage_id_lst=None):
        """read area of each basin/unit"""
        return self.read_attr_xrdataset(gage_id_lst, ["area"])

    def read_mean_prcp(self, gage_id_lst=None, unit="mm/d"):
        """read mean precipitation of each basin
        default unit is mm/d, but one can chose other units and we will convert the unit to the specified unit

        Parameters
        ----------
        gage_id_lst : list, optional
            the list of gage ids, by default None
        unit : str, optional
            the unit of precipitation, by default "mm/d"

        Returns
        -------
        xr.Dataset
            the mean precipitation of each basin
        """
        pre_mm_syr = self.read_attr_xrdataset(gage_id_lst, ["pre_mm_syr"])
        da = pre_mm_syr["pre_mm_syr"]
        # Convert the unit to the specified unit, pre_mm_syr means yearly precipitation
        if unit in ["mm/d", "mm/day"]:
            converted_data = da / 365
        elif unit in ["mm/h", "mm/hour"]:
            converted_data = da / 8760
        elif unit in ["mm/3h", "mm/3hour"]:
            converted_data = da / (8760 / 3)
        elif unit in ["mm/8d", "mm/8day"]:
            converted_data = da / (365 / 8)
        else:
            raise ValueError(
                "unit must be one of ['mm/d', 'mm/day', 'mm/h', 'mm/hour', 'mm/3h', 'mm/3hour', 'mm/8d', 'mm/8day']"
            )

        # Set the units attribute
        converted_data.attrs["units"] = unit
        # Assign the modified DataArray back to the Dataset
        pre_mm_syr["pre_mm_syr"] = converted_data
        return pre_mm_syr


class SelfMadeHydroDataset_PQ(SelfMadeHydroDataset):
    def __init__(self, data_path, download=False, time_unit=None):
        super().__init__(data_path, download, time_unit)

    def cache_timeseries_xrdataset(self, t_range=None, **kwargs):
        """Save all timeseries data in separate Parquet files for each time unit.

        Parameters
        ----------
        t_range : list, optional
            Time range for the data, by default ["1980-01-01", "2023-12-31"]
        kwargs : dict, optional
            batchsize -- Number of basins to process per batch, by default 100
            time_units -- List of time units to process, by default None
            start0101_freq -- for freq setting, if the start date is 01-01, set True, by default False
        """
        time_units = kwargs.get("time_units", self.time_unit) or [
            "1D"
        ]  # Default to ["1D"] if not specified or if time_units is None
        start0101_freq = kwargs.get("start0101_freq", False)

        variables = self.get_timeseries_cols()
        basins = self.camels_sites["basin_id"].values
        for time_unit in time_units:
            if t_range is None:
                if time_unit != "3h":
                    t_range = ["1980-01-01", "2023-12-31"]
                else:
                    t_range = ["1980-01-01 01", "2023-12-31 22"]
            data = self.read_timeseries(
                object_ids=basins,
                t_range_list=t_range,
                relevant_cols=variables[
                    time_unit
                ],  # Ensure we use the right columns for the time unit
                time_units=[
                    time_unit
                ],  # Pass the time unit to ensure correct data retrieval
                start0101_freq=start0101_freq,
            )
            pl_df = pl.concat(data[time_unit])
            # Save the dataset to a Parquet file for the current batch and time unit
            prefix_ = self._get_ts_file_prefix_(self.dataset_name, self.version)
            batch_file_path = os.path.join(
                CACHE_DIR,
                f"{prefix_}timeseries_{time_unit}_batch_{basins[0]}_{basins[-1]}.parquet",
            )
            pl_df.write_parquet(batch_file_path)

    def read_timeseries(
        self, object_ids=None, t_range_list: list = None, relevant_cols=None, **kwargs
    ) -> dict:
        """
        Returns a dictionary containing data with different time scales.

        Parameters
        ----------
        object_ids : list, optional
            List of object IDs. Defaults to None.
        t_range_list : list, optional
            List of time ranges. Defaults to None.
        relevant_cols : list, optional
            List of relevant columns. Defaults to None.
        **kwargs : dict, optional
            Additional keyword arguments.

        Returns
        -------
        dict
            A dictionary containing data with different time scales.
        """
        time_units = kwargs.get("time_units", ["1D"])
        start0101_freq = kwargs.get("start0101_freq", False)

        results = {}

        for time_unit in time_units:
            # whether to convert the time to UTC, for 1D time unit, default set False,
            # and for 3h time unit, set True
            offset_to_utc = time_unit == "3h"
            if offset_to_utc:
                basinoutlets_path = os.path.join(
                    self.data_source_description["SHAPE_DIR"], "basinoutlets.shp"
                )
                try:
                    offset_dict = calculate_basin_offsets(basinoutlets_path)
                except:
                    raise FileNotFoundError(
                        f"basinoutlets.shp not found in {basinoutlets_path}."
                    )
            ts_dir = self._get_ts_dir(
                self.data_source_description["TS_DIRS"], time_unit
            )
            if start0101_freq:
                t_range = generate_start0101_time_range(
                    start_time=t_range_list[0], end_time=t_range_list[-1], freq="1h"
                )
            else:
                t_range = pd.date_range(
                    start=t_range_list[0], end=t_range_list[-1], freq="1h"
                )
            xk_list = []
            for k in tqdm(
                range(len(object_ids)), desc=f"Reading timeseries data with {time_unit}"
            ):
                prefix_ = self._get_ts_file_prefix_(self.dataset_name, self.version)
                ts_file = os.path.join(ts_dir, prefix_ + object_ids[k] + ".csv")
                if "s3://" in ts_file:
                    with conf.FS.open(ts_file, mode="rb") as f:
                        ts_data = pl.read_csv(f, schema_overrides={"time": pl.Datetime})
                        ts_data = ts_data.with_columns(
                            pl.col(pl.String).cast(pl.Float32)
                        )
                else:
                    ts_data = pl.read_csv(
                        ts_file, schema_overrides={"time": pl.Datetime}
                    )
                    ts_data = ts_data.with_columns(pl.col(pl.String).cast(pl.Float32))
                date = pd.to_datetime(ts_data["time"]).values
                if offset_to_utc:
                    date = date - np.timedelta64(offset_dict[object_ids[k]], "h")
                # 由于UTC时区对应问题，会出现时间错位进而丢失大量数据
                offset_date_np = np.intersect1d(date, t_range, return_indices=True)
                ts_data = ts_data.pipe(
                    self._read_timeseries_1basin1var, ts_data.columns[1:]
                )[offset_date_np[1]]
                ts_data = ts_data.with_columns(
                    [
                        pl.Series(np.repeat(object_ids[k], len(ts_data))).alias(
                            "basin_id"
                        )
                    ]
                )
                ts_data_id = ts_data[np.append(relevant_cols, ["basin_id", "time"])]
                ts_data_id = ts_data_id.with_columns(
                    pl.col(pl.Float64).cast(pl.Float32)
                )
                xk_list.append(ts_data_id)
            results[time_unit] = xk_list
        return results

    def read_ts_xrdataset(
        self,
        gage_id_lst: list = None,
        t_range: list = None,
        var_lst: list = None,
        **kwargs,
    ) -> dict:
        """
        Read time-series xarray dataset from multiple NetCDF files and organize them by time units.

        Parameters:
        ----------
        gage_id_lst: list - List of gage IDs to select.
        t_range: list - List of two elements [start_time, end_time] to select time range.
        var_lst: list - List of variables to select.
        **kwargs: Additional arguments.

        Returns:
        ----------
        dict: A dictionary where each key is a time unit and each value is an xarray.Dataset containing the selected gage IDs, time range, and variables.
        """
        time_units = kwargs.get("time_units", self.time_unit)
        if var_lst is None:
            return None
        if ("basin_id" not in var_lst) | ("time" not in var_lst):
            var_lst.extend(["basin_id", "time"])
        # Initialize a dictionary to hold datasets for each time unit
        datasets_by_time_unit = {}

        prefix_ = self._get_ts_file_prefix_(self.dataset_name, self.version)

        for time_unit in time_units:
            # Collect batch files specific to the current time unit
            batch_files = [
                os.path.join(CACHE_DIR, f)
                for f in os.listdir(CACHE_DIR)
                if re.match(
                    rf"^{prefix_}timeseries_{time_unit}_batch_[A-Za-z0-9_]+_[A-Za-z0-9_]+\.parquet$",
                    f,
                )
            ]

            if not batch_files:
                # Cache the data if no batch files are found for the current time unit
                self.cache_timeseries_xrdataset(**kwargs)
                batch_files = [
                    os.path.join(CACHE_DIR, f)
                    for f in os.listdir(CACHE_DIR)
                    if re.match(
                        rf"^{prefix_}timeseries_{time_unit}_batch_[A-Za-z0-9_]+_[A-Za-z0-9_]+\.parquet$",
                        f,
                    )
                ]
            selected_datasets = []
            for batch_file in batch_files:
                ds = pl.scan_parquet(batch_file)
                all_vars = ds.collect_schema().names()
                if any(var not in all_vars for var in var_lst):
                    raise ValueError(f"var_lst must all be in {all_vars}")
                # split ds["basin_id"] out to avoid performance problem
                basin_ids = ds.select("basin_id").unique(maintain_order=True).collect()
                if valid_gage_ids := [
                    gid for gid in gage_id_lst if gid in basin_ids.to_numpy()
                ]:
                    pl_t_range = pl.datetime_range(
                        start=pd.to_datetime(t_range[0]),
                        end=pd.to_datetime(t_range[1]),
                        interval="1h",
                        eager=True,
                    )
                    ds_selected = (
                        ds.select(var_lst)
                        .filter(
                            pl.col("basin_id").is_in(valid_gage_ids),
                            pl.col("time").is_in(pl_t_range),
                        )
                        .collect()
                    )
                    selected_datasets.append(ds_selected)
            # If any datasets were selected, concatenate them along the "basin" dimension
            if selected_datasets:
                datasets_by_time_unit[time_unit] = pl.concat(selected_datasets)
            else:
                datasets_by_time_unit[time_unit] = pl.DataFrame()
        return datasets_by_time_unit

    def _read_timeseries_1basin1var(self, ts_data, relevant_col):
        if "precipitation" in ts_data.columns:
            prcp = ts_data["precipitation"].to_numpy()
            prcp[prcp < 0] = 0.0
            ts_data = ts_data.with_columns(
                [pl.Series(prcp).cast(pl.Float32).alias("precipitation")]
            )
        evap_prcp_cols = [
            col for col in ts_data.columns if col in ERA5LAND_ET_REALATED_VARS
        ]
        if len(evap_prcp_cols) > 0:
            ts_data = ts_data.with_columns(
                [
                    pl.when(pl.col(evap_prcp_cols) > 0)
                    .then(pl.col(evap_prcp_cols))
                    .otherwise(pl.col(evap_prcp_cols) * -1)
                ]
            )
            ts_data = ts_data.with_columns([pl.col(evap_prcp_cols).cast(pl.Float32)])
        modis_et_cols = [col for col in ts_data.columns if col in MODIS_ET_PET_8D_VARS]
        if len(modis_et_cols) > 0:
            ts_data = ts_data.pipe(self._adjust_modis_et_pet, modis_et_cols)
        return ts_data.with_columns(ts_data[relevant_col])

    def _adjust_modis_et_pet(self, ts_data, relevant_col):
        modis_values = ts_data[relevant_col]
        modis_dates = pd.to_datetime(ts_data["time"].to_numpy())
        for idx, current_date in enumerate(modis_dates):
            # Check if the date is prior to or on January 1st
            if current_date.month == 1 and current_date.day == 1:
                if idx == 0:
                    # First day is January 1st, no previous date to scale from
                    continue
                    # Get the previous date
                previous_date = modis_dates[idx - 1]
                # Calculate the number of days between the previous date and January 1st
                delta_days = (current_date - previous_date).days

                # Adjust the MODIS value based on the number of days between the previous date and January 1st
                if delta_days > 0:
                    modis_values[idx - 1] = modis_values[idx - 1] * 8 / delta_days
        # NOTE: MODIS ET values are ACTUALLY in 0.1mm/day, so we need to convert to mm/day
        return ts_data.with_columns((modis_values * 0.1).cast(pl.Float32).get_columns())
