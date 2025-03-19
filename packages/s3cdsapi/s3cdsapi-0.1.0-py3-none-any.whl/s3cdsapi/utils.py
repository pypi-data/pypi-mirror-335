#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 11:28:40 2023

@author: mike
"""
import os
import pathlib
import booklet
import numpy as np
from hashlib import blake2s
import urllib3
import urllib.parse
from urllib3.util import Retry, Timeout

# import product_params
from . import product_params

##########################################
### Parameters

file_naming_str = '{product}.{variable}.{lat_min:.1f}!{lon_min:.1f}!{lat_max:.1f}!{lon_max:.1f}.{from_date}!{to_date}.{job_hash}.{ext}'

key_hash_len = 11
chunk_size = 2**21

### cdsapi
# headers = {
#     'PRIVATE-TOKEN': '{key}'
#     }

url_endpoint = 'https://cds.climate.copernicus.eu/api'
jobs_url = '{url_endpoint}/retrieve/v1/jobs?limit=100'
job_status_url = '{url_endpoint}/retrieve/v1/jobs/{job_id}'
job_results_url = '{url_endpoint}/retrieve/v1/jobs/{job_id}/results'
job_delete_url = '{url_endpoint}/retrieve/v1/jobs/{job_id}'
request_url = '{url_endpoint}/retrieve/v1/processes/{product}/execute/'

#################################################
### Functions


def get_value(file_path, key):
    """

    """
    with booklet.open(file_path) as f:
        value = f.get(key)

    return value


def hash_key(key):
    """

    """
    return blake2s(key, digest_size=key_hash_len).digest()


def process_local_paths(save_path):
    """

    """
    if isinstance(save_path, str):
        save_path = pathlib.Path(save_path)
    elif not isinstance(save_path, pathlib.Path):
        raise TypeError('save_path must be a str or a pathlib.Path.')

    if save_path.is_dir():
        if not save_path.exists():
            raise ValueError('Directory does not exist.')
        staged_file_path = save_path.joinpath('staged.blt')
        save_path = save_path
    else:
        staged_file_path = save_path
        save_path = save_path.parent

    return save_path, staged_file_path


def make_file_name(request_model, job_hash, product):
    """

    """
    variable = request_model.variable[0].value

    year0 = request_model.year[0]
    month0 = request_model.month[0].value
    day0 = request_model.day[0].value
    from_date = f'{year0}-{month0}-{day0}'

    year1 = request_model.year[-1]
    month1 = request_model.month[-1].value
    day1 = request_model.day[-1].value
    to_date = f'{year1}-{month1}-{day1}'

    lat_min, lon_min, lat_max, lon_max = request_model.area

    data_format = request_model.data_format.value
    if data_format == 'netcdf':
        ext = 'nc'
    elif data_format == 'grib':
        ext = 'grib'
    else:
        raise ValueError('How did this happen!')

    file_name = file_naming_str.format(product=product, variable=variable, lat_min=lat_min, lon_min=lon_min, lat_max=lat_max, lon_max=lon_max, job_hash=job_hash, ext=ext, from_date=from_date, to_date=to_date)

    return file_name


def time_request(from_date1, to_date1):
    """

    """
    # from_date1 = from_date1 + pd.DateOffset(days=1)
    from_day = from_date1.day
    to_day = to_date1.day
    from_month = from_date1.month
    to_month = to_date1.month
    from_year = from_date1.year
    to_year = to_date1.year

    if from_year == to_year:
        years1 = [from_year]
        months1 = np.arange(from_month, to_month+1)

        if from_month == to_month:
            days1 = np.arange(from_day, to_day+1)
        else:
            days1 = np.arange(1, 32)
    else:
        years1 = np.arange(from_year, to_year+1)
        months1 = np.arange(1, 13)
        days1 = np.arange(1, 32)

    days = ['{:02d}'.format(d) for d in days1]
    months = ['{:02d}'.format(m) for m in months1]
    years = ['{:04d}'.format(y) for y in years1]

    return {'year': years, 'month': months, 'day': days, 'time': product_params.times}


def session(max_pool_connections: int = 10, max_attempts: int=3, timeout: int=120):
    """
    Function to setup a urllib3 pool manager for url downloads.

    Parameters
    ----------
    max_pool_connections : int
        The number of simultaneous connections for the S3 connection.
    max_attempts: int
        The number of retries if the connection fails.
    timeout: int
        The timeout in seconds.

    Returns
    -------
    Pool Manager object
    """
    timeout = urllib3.util.Timeout(timeout)
    retries = Retry(
        total=max_attempts,
        backoff_factor=1,
        )
    http = urllib3.PoolManager(num_pools=max_pool_connections, timeout=timeout, retries=retries)

    return http


def concat(input_files, output_file, buffer_size: int=2**20):
    """
    Concatenate multiple binary files to another file. Must be on disk as all files must have file descriptors. This can only be used on Linux OS's. This is primarily for concatenating grib files. This will definitely not work for netcdf4 files!

    Parameters
    ----------
    input_files : iterator of file objects that have file descriptors
    output_file : object that can be opened by "open" and has a file descriptor
    buffer_size : int
        The read/write buffer size.

    Returns
    -------
    None
    """
    with open(output_file, 'wb') as f:
        for file in input_files:
            with open(file, 'rb') as f2:
                b = buffer_size
                while b != 0:
                    b = os.sendfile(f.fileno(), f2.fileno(), None, buffer_size)




































































