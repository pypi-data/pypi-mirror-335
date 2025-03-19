#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 09:51:59 2025

@author: mike
"""
import io
import pathlib
import os
import pandas as pd
import numpy as np
import booklet
from time import sleep, time
import copy
import shutil
import msgspec
from typing import Set, Optional, Dict, Tuple, List, Union, Any, Annotated
from s3func import S3Session, HttpSession
import urllib3
# import urllib.parse
# from urllib3.util import Retry, Timeout
urllib3.disable_warnings()

# import utils, models, product_params
from . import utils, models, product_params

################################################
### Parameters



###############################################
### Classes


class Manager:
    """

    """
    ## Initialization
    def __init__(self, save_path: str | pathlib.Path, cds_url_endpoint: str, cds_key: str, s3_base_key: str=None, **s3_kwargs):
        """
        Class to download CDS data via their cdsapi. This is just a wrapper on top of cdsapi that makes it more useful as an API. The user needs to register by following the procedure here: https://cds.climate.copernicus.eu/api-how-to.

        Parameters
        ----------
        save_path : str
            The path to save the downloaded files.
        cds_url_endpoint : str
            The endpoint URL provided after registration.
        cds_key: str
            The key provided after registration.
        s3_base_key: str or None
            The base path where the S3 files will be saved if S3 credentials are provided.
        s3_kwargs:
            Any kwargs passed to S3Session of the s3func package. The required kwargs include access_key_id, access_key, and bucket.

        Returns
        -------
        Manager object
        """
        save_path, staged_file_path = utils.process_local_paths(save_path)
        job_file_path = save_path.joinpath('jobs.blt')
        if not job_file_path.exists():
            with booklet.open(job_file_path, 'n', 'str', 'str'):
                pass

        if not staged_file_path.exists():
            with booklet.open(staged_file_path, 'n', 'str', 'bytes'):
                pass

        if s3_kwargs:
            # if not isinstance(access_key, str) and not isinstance(bucket, str) and not isinstance(base_key, str):
            #     raise TypeError('If access_key_id is a string, then access_key, bucket, and base_key must also be strings.')

            # kwargs.update(dict(access_key_id=access_key_id, access_key=access_key, bucket=bucket))

            if not isinstance(s3_base_key, str):
                raise TypeError('If kwargs is passed, then s3_base_key must be a string.')

            s3_session_kwargs = s3_kwargs

            if not s3_base_key.endswith('/'):
                s3_base_key += '/'
            s3_base_key = s3_base_key
        else:
            s3_session_kwargs = None
            s3_base_key = None

        self.s3_session_kwargs = s3_session_kwargs
        self.s3_base_key = s3_base_key

        self.url_endpoint = cds_url_endpoint
        self.headers = {'PRIVATE-TOKEN': f'{cds_key}'}

        self.save_path = save_path
        self.staged_file_path = staged_file_path
        self.job_file_path = job_file_path

        setattr(self, 'available_variables', product_params.available_variables)
        setattr(self, 'available_products', list(product_params.available_variables.keys()))
        setattr(self, 'available_freq_intervals', product_params.available_freq_intervals)
        setattr(self, 'available_product_types', product_params.product_types)
        setattr(self, 'available_pressure_levels', product_params.pressure_levels)


    def _input_checks(self, product, variables, from_date, to_date, bbox, freq_interval, product_types, pressure_levels, output_format):
        """

        """
        ## Prep and checks
        if product not in self.available_variables.keys():
            raise ValueError('product is not available.')

        # Parameters/variables
        if isinstance(variables, str):
            variables1 = [variables]
        elif isinstance(variables, list):
            variables1 = variables.copy()
        else:
            raise TypeError('variables must be a str or a list of str.')

        for p in variables1:
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
        if isinstance(bbox, (list, tuple)):
            if len(bbox) != 4:
                raise ValueError('bbox must be a list/tuple of 4 floats.')
            else:
                bbox1 = np.round(bbox, 1).tolist()
        else:
            raise TypeError('bbox must be a list/tuple of 4 floats.')

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

        return variables1, product_types1, bbox1, pressure_levels1, dates1, from_date1


    def stage_jobs(self, product: str, variables: str | List[str], from_date: str | pd.Timestamp, to_date: str | pd.Timestamp, bbox: List[float], freq_interval: str, product_types: str | List[str]=None, pressure_levels: str | List[str]=None, output_format: str='netcdf', check_existing_files=True):
        """

        """
        variables1, product_types1, bbox1, pressure_levels1, dates1, from_date1 = self._input_checks(product, variables, from_date, to_date, bbox, freq_interval, product_types, pressure_levels, output_format)

        model_type = models.model_types[product]

        existing_job_hashes = set()
        if check_existing_files:
            if output_format == 'netcdf':
                suffix = '.nc'
            else:
                suffix = '.grib'
            if self.s3_session_kwargs is None:
                for file in self.save_path.iterdir():
                    if file.is_file():
                        if file.suffix == suffix:
                            job_hash = file.name.split('.')[-2]
                            existing_job_hashes.add(job_hash)
            else:
                s3_session = S3Session(**self.s3_session_kwargs)
                resp = s3_session.list_objects(self.s3_base_key)
                for obj in resp.iter_objects():
                    key = obj['key']
                    file_name = key.split('/')[-1]
                    job_hash = file_name.split('.')[-2]
                    existing_job_hashes.add(job_hash)

        ## Add requests
        with booklet.open(self.staged_file_path, 'w') as sf:

            for var in variables1:
                dict1 = {'type': model_type, 'data_format': output_format, 'variable': [var], 'area': bbox1, 'download_format': 'unarchived'}

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

                    time_dict = utils.time_request(fdate, tdate)

                    dict2.update(time_dict)

                    m1 = models.convert(dict2)
                    b1 = models.dumps(m1)
                    job_hash = utils.hash_key(b1).hex()
                    # print(m1)
                    # print(request_hex)
                    # print(b1)

                    if job_hash not in sf and job_hash not in existing_job_hashes:
                        sf[job_hash] = b1

        return self.staged_file_path


    def read_staged_file(self):
        """

        """
        if self.staged_file_path.exists():
            dict1 = {}
            with booklet.open(self.staged_file_path) as f:
                for job_hash, request_bytes in f.items():
                    request_dict = msgspec.json.decode(request_bytes)
                    dict1[job_hash] = request_dict

            return dict1
        else:
            raise ValueError('file does not exist.')


    def clear_jobs(self, all_jobs=False, only_failed=False):
        """
        When all_jobs is False, then only the jobs that are not in the jobs file will be removed. Otherwise, all jobs will be removed.
        """
        jobs_list = self._get_jobs_list()

        http_session = utils.session()

        remove_job_ids = set()
        job_ids = set()

        if not all_jobs:
            with booklet.open(self.job_file_path, 'r') as jf:
                for jf_job_id in jf.keys():
                    job_ids.add(jf_job_id)

        for job_dict in jobs_list:
            job_id = job_dict['jobID']
            status = job_dict['status']

            job_id_bool = job_id in job_ids
            failed_bool = status == 'failed'

            if all_jobs:
                if only_failed:
                    if failed_bool:
                        remove_job_ids.add(job_id)
                else:
                    remove_job_ids.add(job_id)
            elif not job_id_bool:
                if only_failed:
                    if failed_bool:
                        remove_job_ids.add(job_id)
                else:
                    remove_job_ids.add(job_id)

        if remove_job_ids:
            with booklet.open(self.job_file_path, 'w') as jf:
                with booklet.open(self.staged_file_path, 'w') as sf:
                    for job_id in remove_job_ids:
                        url = utils.job_delete_url.format(url_endpoint=self.url_endpoint, job_id=job_id)
                        resp = http_session.request('delete', url, headers=self.headers)
                        if resp.status // 100 != 2:
                            raise urllib3.exceptions.HTTPError(resp.json())

                        sleep(1) # Don't hit the API too fast
                        if job_id in job_ids:
                            job_hash = jf[self.job_id]
                            del jf[self.job_id]

                            if job_hash in sf:
                                del sf[job_hash]

        return remove_job_ids


    def submit_jobs(self, n_jobs_queued=15):
        """

        """
        jobs_list = self._get_jobs_list()

        n_queued = 0
        for job_dict in jobs_list:
            if job_dict['status'] == 'accepted':
                n_queued += 1

        if n_queued < n_jobs_queued:
            # print(f'-- {extra_n_queued} jobs will be submitted')

            http_session = utils.session()

            job_hashes = set()
            submitted_jobs = set()
            with booklet.open(self.staged_file_path, 'r') as sf:
                with booklet.open(self.job_file_path, 'w') as jf:
                    for job_id, jf_job_hash in jf.items():
                        job_hashes.add(jf_job_hash)

                    for job_hash, request_bytes in sf.items():
                        if n_queued == n_jobs_queued:
                            break

                        if job_hash not in job_hashes:
                            request_model = models.loads(request_bytes)
                            model_type = request_model.__class__.__name__
                            product = models.inv_model_types[model_type]
                            request_url = utils.request_url.format(url_endpoint=self.url_endpoint, product=product)

                            request_dict = msgspec.to_builtins(request_model)

                            resp = http_session.request('post', request_url, json={'inputs': request_dict}, headers=self.headers)
                            resp_dict = resp.json()
                            if resp.status // 100 != 2:
                                print(resp_dict)
                            else:
                                job_id = resp_dict['jobID']
                                jf[job_id] = job_hash
                                job_hashes.add(job_hash)
                                submitted_jobs.add(job_hash)
                                n_queued += 1

                            sleep(2) # Submitting jobs too quickly makes CDS angry

            return submitted_jobs
        else:
            return set()


    def _get_jobs_list(self):
        """

        """
        http_session = utils.session()
        url = utils.jobs_url.format(url_endpoint=self.url_endpoint)
        jobs_resp = http_session.request('get', url, headers=self.headers)
        if jobs_resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(jobs_resp.json())

        jobs_dict = jobs_resp.json()
        n_jobs = jobs_dict['metadata']['totalCount']
        if n_jobs == 100:
            print('The number of jobs on the server is greater than 100. Please delete finished/failed jobs using clear_jobs.')

        jobs_list = jobs_dict['jobs']

        return jobs_list


    def get_jobs(self):
        """

        """
        jobs_list = self._get_jobs_list()
        jobs = {}

        n_missing_jobs = 0
        with booklet.open(self.job_file_path) as jf:
            for job_dict in jobs_list:
                # if job_dict['status'] == 'successful':
                #     d
                job_id = job_dict['jobID']
                job_hash = jf.get(job_id)
                if job_hash:
                    job = Job(job_dict, job_hash, self.url_endpoint, self.headers, self.save_path, self.staged_file_path, self.job_file_path, self.s3_session_kwargs, self.s3_base_key)
                    jobs[job_hash] = job
                else:
                    n_missing_jobs += 1

        if n_missing_jobs> 0:
            print(f'There are {n_missing_jobs} jobs that are not in the jobs file file.')

        return jobs


    def run_jobs(self, n_jobs_queued=15):
        """

        """
        n_completed = 0
        while True:
            _ = self.submit_jobs(n_jobs_queued=n_jobs_queued)
            sleep(2)
            jobs = self.get_jobs()
            if len(jobs) == 0:
                break

            ## Check and remove failed jobs
            failed_bool = False
            for job_hash, job in jobs.items():
                if job.status == 'failed':
                    failed_bool = True

            if failed_bool:
                _ = self.clear_jobs(all_jobs=False, only_failed=True)
                sleep(2)
                jobs = self.get_jobs()

            ## If any are successful, then download
            for job_hash, job in jobs.items():
                if job.status == 'successful':
                    results_path = job.download_results()
                    print(f'{job.file_name} completed')
                    n_completed += 1

            sleep(60)

        return n_completed


class Job:
    """

    """
    def __init__(self, job_dict, job_hash, url_endpoint, headers, save_path, staged_file_path, job_file_path, s3_session_kwargs, s3_base_key):
        """

        """
        self.s3_base_key = s3_base_key
        self.s3_session_kwargs = s3_session_kwargs
        self.job_hash = job_hash
        self.save_path = save_path
        self.staged_file_path = staged_file_path
        self.job_file_path = job_file_path
        self.url_endpoint = url_endpoint
        self.headers = headers
        self.product = job_dict['processID']
        self.type = job_dict['type']
        self.job_id = job_dict['jobID']
        self.status = job_dict['status']
        self.created = job_dict['created']
        if 'started' in job_dict:
            self.started = job_dict['started']
        else:
            self.started = None
        if 'finished' in job_dict:
            self.finished = job_dict['finished']
        else:
            self.finished = None
        if 'updated' in job_dict:
            self.updated = job_dict['updated']
        else:
            self.updated = None

        results0 = job_dict['metadata']['results']

        if self.status == 'successful':
            if 'asset' in results0:
                self.results = job_dict['metadata']['results']['asset']['value']
                self.error = None
            else:
                self.results = None
                self.error = job_dict['metadata']['results']

        elif self.status == 'failed':
            self.results = None
            self.error = job_dict['metadata']['results']
        else:
            self.results = None
            self.error = None

        request_bytes = utils.get_value(self.staged_file_path, self.job_hash)
        request_model = models.loads(request_bytes)

        file_name = utils.make_file_name(request_model, self.job_hash, self.product)
        self.file_name = file_name


    def __repr__(self):
        """

        """
        return f"""
        job_id:   {self.job_id}
        status:   {self.status}
        job_hash: {self.job_hash}
        product:  {self.product}
        """


    def update(self):
        """

        """
        if self.status == 'dismissed':
            raise ValueError('Job has been deleted.')

        http_session = utils.session()
        url = utils.job_status_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id)
        jobs_resp = http_session.request('get', url, headers=self.headers)
        if jobs_resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(jobs_resp.json())

        job_dict = jobs_resp.json()

        if self.status != job_dict['status']:
            self.status = job_dict['status']
            if 'started' in job_dict:
                self.started = job_dict['started']
            else:
                self.started = None
            if 'finished' in job_dict:
                self.finished = job_dict['finished']
            else:
                self.finished = None
            if 'updated' in job_dict:
                self.updated = job_dict['updated']
            else:
                self.updated = None

            if self.status == 'successful':
                url = utils.job_results_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id)
                jobs_resp = http_session.request('get', url, headers=self.headers)
                results0 = jobs_resp.json()
                if jobs_resp.status // 100 != 2:
                    self.error = results0
                    self.results = None
                else:
                    self.results = results0['asset']['value']
                    self.error = None

            elif self.status == 'failed':
                url = utils.job_results_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id)
                jobs_resp = http_session.request('get', url, headers=self.headers)
                self.error = jobs_resp.json()
                self.results = None

            ## Remove from Queue file
            if self.status in ('successful', 'failed'):
                # job_hash = utils.get_value(self.queue_file_path, self.job_id)
                # if job_hash:
                with booklet.open(self.job_file_path, 'w') as f:
                    del f[self.job_id]


    def delete(self):
        """

        """
        http_session = utils.session()
        url = utils.job_delete_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id)
        resp = http_session.request('delete', url, headers=self.headers)
        if resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(resp.json())

        self.status = 'dismissed'

        ## Remove from Job file and staged file
        with booklet.open(self.staged_file_path, 'w') as sf:
            with booklet.open(self.job_file_path, 'w') as jf:
                if self.job_id in jf:
                    job_hash = jf[self.job_id]
                    del jf[self.job_id]

                    if job_hash in sf:
                        del sf[job_hash]


    def _download_results_local(self, chunk_size=2**21, delete_job=True):
        """

        """
        if self.results is None:
            raise ValueError('No results to download.')

        file_path = self.save_path.joinpath(self.file_name)

        http_session = utils.session()
        download_url = self.results['href']
        resp = http_session.request('get', download_url, preload_content=False)
        if resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(resp.json())

        # start = time()
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(resp, f, chunk_size)
        # end = time()
        # print(end - start)

        resp.release_conn()

        ## Remove from server
        if delete_job:
            self.delete()

        return file_path


    def _download_results_s3(self, chunk_size=2**21, delete_job=True):
        """

        """
        if self.results is None:
            raise ValueError('No results to download.')

        http_session = utils.session()
        download_url = self.results['href']
        resp = http_session.request('get', download_url, preload_content=False)
        if resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(resp.json())

        file_path = self.save_path.joinpath(self.file_name)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(resp, f, chunk_size)

        resp.release_conn()

        key_name = self.s3_base_key + self.file_name
        s3_session = S3Session(**self.s3_session_kwargs)
        # reader = io.BufferedReader(resp, chunk_size)
        put_resp = s3_session.put_object(key_name, open(file_path, 'rb'))
        if put_resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(put_resp.error)

        os.unlink(file_path)

        ## Remove from server
        if delete_job:
            self.delete()

        return key_name


    def download_results(self, chunk_size=2**21, delete_job=True):
        """

        """
        if self.s3_session_kwargs is None:
            path = self._download_results_local(chunk_size, delete_job)
        else:
            path = self._download_results_s3(chunk_size, delete_job)

        return path





























































































