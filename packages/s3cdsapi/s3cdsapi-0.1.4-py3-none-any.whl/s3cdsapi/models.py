#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 13:35:57 2025

@author: mike
"""
import msgspec
import enum
from typing import Set, Optional, Dict, Tuple, List, Union, Any, Annotated

# import product_params
from . import product_params

######################################################
### Enums

months = enum.Enum('months', ((v, v) for v in product_params.months))

days = enum.Enum('days', ((v, v) for v in product_params.days))

times = enum.Enum('times', ((v, v) for v in product_params.times))

era5_land_vars = enum.Enum('era5_land_vars', ((v, v) for v in product_params.available_variables['reanalysis-era5-land']))

era5_sl_vars = enum.Enum('era5_sl_vars', ((v, v) for v in product_params.available_variables['reanalysis-era5-single-levels']))

era5_pl_vars = enum.Enum('era5_pl_vars', ((v, v) for v in product_params.available_variables['reanalysis-era5-pressure-levels']))

data_formats = enum.Enum('data_formats', ((v, v) for v in ('netcdf', 'grib')))

download_formats = enum.Enum('download_formats', ((v, v) for v in ('unarchived', 'zip')))

era5_product_types = enum.Enum('era5_product_types', ((v, v) for v in product_params.product_types['reanalysis-era5-pressure-levels']))

era5_pressure_levels = enum.Enum('era5_pressure_levels', ((str(v), str(v)) for v in product_params.pressure_levels['reanalysis-era5-pressure-levels']))

model_types = {
    'reanalysis-era5-land': 'era5_land',
    'reanalysis-era5-single-levels': 'era5_single_levels',
    'reanalysis-era5-pressure-levels': 'era5_pressure_levels',
    }

inv_model_types = {v: k for k, v in model_types.items()}


#####################################################
### Helper functions


def round_area(area):
    return tuple(round(a, 1) for a in area)


#####################################################
### Models

Point = Annotated[float, msgspec.Meta(ge=-180, le=180)]


class era5_land(msgspec.Struct, tag=True):
    """

    """
    variable: List[era5_land_vars]
    year: List[str]
    month: List[months]
    day: List[days]
    time: List[times]
    data_format: data_formats
    download_format: download_formats
    area: Tuple[Point, Point, Point, Point]

    # def __post_init__(self):
    #     self.area = round_area(self.area)


class era5_single_levels(msgspec.Struct, tag=True):
    """

    """
    product_type: List[era5_product_types]
    variable: List[era5_sl_vars]
    year: List[str]
    month: List[months]
    day: List[days]
    time: List[times]
    data_format: data_formats
    download_format: download_formats
    area: Tuple[Point, Point, Point, Point]

    # def __post_init__(self):
    #     self.area = round_area(self.area)


class era5_pressure_levels(msgspec.Struct, tag=True):
    """

    """
    product_type: List[era5_product_types]
    variable: List[era5_pl_vars]
    year: List[str]
    month: List[months]
    day: List[days]
    time: List[times]
    pressure_level: List[era5_pressure_levels]
    data_format: data_formats
    download_format: download_formats
    area: Tuple[Point, Point, Point, Point]

    # def __post_init__(self):
    #     self.area = round_area(self.area)


RequestModels = era5_land | era5_single_levels | era5_pressure_levels


loads = msgspec.json.Decoder(RequestModels).decode
dumps = msgspec.json.Encoder().encode


def convert(data):
    """

    """
    return msgspec.convert(data, RequestModels)






























































































