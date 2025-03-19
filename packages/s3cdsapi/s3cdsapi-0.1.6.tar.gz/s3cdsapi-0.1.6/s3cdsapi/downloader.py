#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 10:32:40 2021

@author: mike
"""
import pathlib
import os
import pandas as pd
import numpy as np
from multiprocessing.pool import ThreadPool, Pool
import concurrent.futures
import cdsapi
import requests
from time import sleep
import copy
import urllib3
urllib3.disable_warnings()

##############################################
### Parameters



########################################
### Helper functions


def download_file(client, name, request, target):
    """

    """
    # r = client.retrieve(name, request)

    # retries = 5
    # while True:
    #     sleep(60)
    #     # r.update()
    #     reply = r.reply
    #     # r.info("Request ID: %s, state: %s" % (reply["request_id"], reply["state"]))
    #     print("Request ID: %s, state: %s" % (reply["request_id"], reply["state"]))

    #     if reply["state"] in ("completed", 'successful'):
    #         break
    #     # elif reply["state"] in ("queued", "running"):
    #     #     # r.info("Request ID: %s, sleep: %s", reply["request_id"], sleep)
    #     #     sleep(300)
    #     elif reply["state"] in ("failed",):
    #         r.error("Message: %s", reply["error"].get("message"))
    #         r.error("Reason:  %s", reply["error"].get("reason"))

    #         print('Request failed with message: {msg}; and reason: {reason}'.format(msg=reply["error"].get("message"), reason=reply["error"].get("reason")))

    #         ## Remove request
    #         r.delete()

    #         if retries > 0:
    #             ## try again
    #             sleep(60)
    #             r = client.retrieve(name, request)
    #         else:
    #             raise Exception('Request failed with message: {msg}; and reason: {reason}'.format(msg=reply["error"].get("message"), reason=reply["error"].get("reason")))

    # r.download(target)

    client.retrieve(name, request, target)

    return target


class Downloader:
    """

    """
    def __init__(self, client, product, request, target):
        """

        """
        self.client = client
        self.product = product
        self.request = request
        self.target = target


    def download(self):
        """

        """
        # target = download_file(self.client, self.product, self.request, self.target)
        self.client.retrieve(self.product, self.request, self.target)

        return self.target



########################################
### Main class


class CDS(object):
    """
    Class to download CDS data via their cdsapi. This is just a wrapper on top of cdsapi that makes it more useful as an API. The user needs to register by following the procedure here: https://cds.climate.copernicus.eu/api-how-to.

    Parameters
    ----------
    url : str
        The endpoint URL provided after registration.
    key: str
        The key provided after registration.
    save_path : str
        The path to save the downloaded files.

    Returns
    -------
    Downloader object
    """
    ## Initialization
    def __init__(self, url, key, save_path, threads=32):
        """
        Class to download CDS data via their cdsapi. This is just a wrapper on top of cdsapi that makes it more useful as an API. The user needs to register by following the procedure here: https://cds.climate.copernicus.eu/api-how-to.

        Parameters
        ----------
        url : str
            The endpoint URL provided after registration.
        key: str
            The key provided after registration.
        save_path : str or pathlib.Path
            The path to save the downloaded files.
        threads : int
            The number of simultaneous download/queued requests. Only one request will be processed at one time, but a user can queue many requests. It's unclear if there is a limit to the number of queued requests per user.

        Returns
        -------
        Downloader object
        """
        if isinstance(save_path, str):
            setattr(self, 'save_path', save_path)
        elif isinstance(save_path, pathlib.Path):
            setattr(self, 'save_path', str(save_path))
        else:
            raise TypeError('save_path must be a str or a pathlib.Path.')

        sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=threads, pool_maxsize=threads)
        sess.mount('https://', adapter)

        client = cdsapi.Client(url=url, key=key, session=sess)

        setattr(self, 'client', client)
        setattr(self, 'available_variables', available_variables)
        setattr(self, 'available_products', list(available_variables.keys()))
        setattr(self, 'available_freq_intervals', available_freq_intervals)
        setattr(self, 'available_product_types', product_types)
        setattr(self, 'available_pressure_levels', pressure_levels)
        setattr(self, 'threads', threads)


    def _processing(self, product: str, variables, from_date, to_date, bbox, freq_interval='Y', product_types=None, pressure_levels=None, output_format='netcdf'):
        """

        """
        if product not in self.available_variables.keys():
            raise ValueError('product is not available.')

        # Parameters/variables
        if isinstance(variables, str):
            params = [variables]
        elif isinstance(variables, list):
            params = variables.copy()
        else:
            raise TypeError('variables must be a str or a list of str.')

        for p in params:
            av = self.available_variables[product]
            if not p in av:
                raise ValueError(p + ' is not one of the available variables for this product.')

        # freq intervals
        if not freq_interval in self.available_freq_intervals:
            raise ValueError('freq_interval must be one of: ' + str(self.available_freq_intervals))

        # Product types
        if product in self.available_product_types:
            if isinstance(product_types, str):
                product_types1 = [product_types]
            elif not isinstance(product_types, list):
                raise TypeError('The requested product has required product_types, but none have been specified.')
            pt_bool = all([p in self.available_product_types[product] for p in product_types1])

            if not pt_bool:
                raise ValueError('Not all requested product_types are in the available_product_types.')
        else:
            product_types1 = None

        # Pressure levels
        if product in self.available_pressure_levels:
            if isinstance(pressure_levels, list):
                pressure_levels1 = pressure_levels
            elif isinstance(pressure_levels, int):
                pressure_levels1 = [pressure_levels]
            else:
                raise TypeError('The requested product has required pressure_levels, but none have been specified.')
            pl_bool = all([p in self.available_pressure_levels[product] for p in pressure_levels1])

            if not pl_bool:
                raise ValueError('Not all requested pressure_levels are in the available_pressure_levels.')
        else:
            pressure_levels1 = None

        ## Parse dates
        if isinstance(from_date, (str, pd.Timestamp)):
            from_date1 = pd.Timestamp(from_date).floor('D')
        else:
            raise TypeError('from_date must be either str or Timestamp.')
        if isinstance(to_date, (str, pd.Timestamp)):
            to_date1 = pd.Timestamp(to_date).floor('D')
        else:
            raise TypeError('to_date must be either str or Timestamp.')

        ## Parse bbox
        if isinstance(bbox, list):
            if len(bbox) != 4:
                raise ValueError('bbox must be a list of 4 floats.')
            else:
                bbox1 = np.round(bbox, 1).tolist()
        else:
            raise TypeError('bbox must be a list of 4 floats.')

        ## Formats
        if output_format not in ['netcdf', 'grib']:
            raise ValueError('output_format must be either netcdf or grib')

        ## Split dates into download chunks
        dates1 = pd.date_range(from_date1, to_date1, freq=freq_interval)

        if dates1.empty:
            raise ValueError('The frequency interval is too long for the input time period. Use a shorter frequency interval.')

        # if from_date1 < dates1[0]:
        #     dates1 = pd.DatetimeIndex([from_date1]).append(dates1)
        if to_date1 > dates1[-1]:
            dates1 = dates1.append(pd.DatetimeIndex([to_date1]))

        return params, product_types1, bbox1, pressure_levels1, dates1, from_date1


    def downloader(self, product: str, variables, from_date, to_date, bbox, freq_interval='Y', product_types=None, pressure_levels=None, output_format='netcdf', zipped=False):
        """
        The method to do the actual downloading of the files. The current maximum queue limit is 32 requests per user and this has been set as the number of threads to use. The cdsapi blocks the threads until they finished downloading. This can take a very long time for many large files...make sure this process can run happily without interruption for a while...
        This method does not check to make sure you do not exceede the CDS extraction limit of 120,000 values, so be sure to make your request of a sane size. When in doubt, just reduce the amount per request by lowering the freq_interval.

        The freq_interval can be 1D or D for daily, 1M or M for monthly, or yearly (Y) with up to 11 years (11Y).
        This extraction resolution is due to the limitations of the cdsapi.

        Parameters
        ----------
        product : str
            The requested product. Look at the available_parameters keys for all options.
        variables : str or list of str
            The requested variables. Look at the available_variables values for all options.
        from_date : str or Timestamp
            The start date of the extraction.
        to_date : str or Timestamp
            The end date of the extraction.
        bbox : list of float
            The bounding box of lat and lon for the requested area. It must be in the order of [upper lat, left lon, lower lat, right lon].
        freq_interval : str
            Pandas frequency string representing the time interval of each request. The freq_interval can be 1D or D for daily, 1M or M for monthly, or yearly (Y) with up to 11 years (11Y).
        product_types : str or list of str
            Some products have product types and if they do they need to be specified. Check the available_product_types object for the available options.
        pressure_levels : int or list of int
            Some products have pressure levels and if they do they need to be specified. Check the available_pressure_levels object for the available options.
        output_format : str
            The output format for the file. Must be either netcdf or grib.

        Returns
        -------
        Iterator of Downloaders
        """
        ## Get input params
        params, product_types1, bbox1, pressure_levels1, dates1, from_date1 = self._processing(product, variables, from_date, to_date, bbox, freq_interval, product_types, pressure_levels, output_format)

        ## Create requests
        # req_list = []
        for p in params:
            dict1 = {'data_format': output_format, 'variable': p, 'area': bbox1}
            if not zipped:
                dict1['download_format'] = 'unarchived'

            if isinstance(product_types1, list):
                dict1['product_type'] = product_types1

            if isinstance(pressure_levels1, list):
                dict1['pressure_level'] = [str(p) for p in pressure_levels1]

            for i, tdate in enumerate(dates1):
                if i == 0:
                    fdate = from_date1
                else:
                    fdate = dates1[i-1] + pd.DateOffset(days=1)

                dict2 = copy.deepcopy(dict1)

                time_dict = time_request(fdate, tdate)

                dict2.update(time_dict)

                file_name = file_naming.format(param=p, from_date=fdate.strftime('%Y%m%d'), to_date=tdate.strftime('%Y%m%d'), product=product, ext=ext_dict[output_format])
                file_path = os.path.join(self.save_path, file_name)

                # req_list.append({'name': product, 'request': dict2, 'target': file_path})
                yield Downloader(self.client, product, dict2, file_path)

        ## Run requests
        # with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
        #     futures = []
        #     for req in req_list:
        #         f = executor.submit(download_file, self.client, req['name'], req['request'], req['target'])
        #         futures.append(f)

        # runs = concurrent.futures.wait(futures)

        # paths = []
        # for run in runs[0]:
        #     paths.append(run.result())

        # print('Finished')

        # return paths


    def download(self, product: str, variables, from_date, to_date, bbox, freq_interval='Y', product_types=None, pressure_levels=None, output_format='netcdf', zipped=False):
        """
        The method to do the actual downloading of the files. The current maximum queue limit is 32 requests per user and this has been set as the number of threads to use. The cdsapi blocks the threads until they finished downloading. This can take a very long time for many large files...make sure this process can run happily without interruption for a while...
        This method does not check to make sure you do not exceede the CDS extraction limit of 120,000 values, so be sure to make your request of a sane size. When in doubt, just reduce the amount per request by lowering the freq_interval.

        The freq_interval can be 1D or D for daily, 1M or M for monthly, or yearly (Y) with up to 11 years (11Y).
        This extraction resolution is due to the limitations of the cdsapi.

        Parameters
        ----------
        product : str
            The requested product. Look at the available_parameters keys for all options.
        variables : str or list of str
            The requested variables. Look at the available_variables values for all options.
        from_date : str or Timestamp
            The start date of the extraction.
        to_date : str or Timestamp
            The end date of the extraction.
        bbox : list of float
            The bounding box of lat and lon for the requested area. It must be in the order of [upper lat, left lon, lower lat, right lon].
        freq_interval : str
            Pandas frequency string representing the time interval of each request. The freq_interval can be 1D or D for daily, 1M or M for monthly, or yearly (Y) with up to 11 years (11Y).
        product_types : str or list of str
            Some products have product types and if they do they need to be specified. Check the available_product_types object for the available options.
        pressure_levels : int or list of int
            Some products have pressure levels and if they do they need to be specified. Check the available_pressure_levels object for the available options.
        output_format : str
            The output format for the file. Must be either netcdf or grib.

        Returns
        -------
        Paths as strings
        """
        ## Get input params
        params, product_types1, bbox1, pressure_levels1, dates1, from_date1 = self._processing(product, variables, from_date, to_date, bbox, freq_interval, product_types, pressure_levels, output_format)

        ## Create requests
        req_list = []
        for p in params:
            dict1 = {'data_format': output_format, 'variable': p, 'area': bbox1}
            if not zipped:
                dict1['download_format'] = 'unarchived'

            if isinstance(product_types1, list):
                dict1['product_type'] = product_types1

            if isinstance(pressure_levels1, list):
                dict1['pressure_level'] = [str(p) for p in pressure_levels1]

            for i, tdate in enumerate(dates1):
                if i == 0:
                    fdate = from_date1
                else:
                    fdate = dates1[i-1] + pd.DateOffset(days=1)

                dict2 = copy.deepcopy(dict1)

                time_dict = time_request(fdate, tdate)

                dict2.update(time_dict)

                file_name = file_naming.format(param=p, from_date=fdate.strftime('%Y%m%d'), to_date=tdate.strftime('%Y%m%d'), product=product, ext=ext_dict[output_format])
                file_path = os.path.join(self.save_path, file_name)

                req_list.append({'name': product, 'request': dict2, 'target': file_path})
                # yield Downloader(self.client, product, dict2, file_path)

        ## Run requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for req in req_list:
                sleep(2)
                f = executor.submit(download_file, self.client, req['name'], req['request'], req['target'])
                futures.append(f)

        runs = concurrent.futures.wait(futures)

        paths = []
        for run in runs[0]:
            paths.append(run.result())

        # print('Finished')

        return paths



