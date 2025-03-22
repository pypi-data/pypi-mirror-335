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
            The base path where the S3 files will be saved if S3 credentials are provided. Backslashes should be used to separate 'directories'.
        s3_kwargs:
            Any kwargs passed to S3Session of the s3func package. The required kwargs include access_key_id, access_key, and bucket.

        Returns
        -------
        Manager object
        """
        save_path, staged_file_path = utils.process_local_paths(save_path)
        # job_file_path = save_path.joinpath('jobs.blt')
        # if not job_file_path.exists():
        #     with booklet.open(job_file_path, 'n', 'str', 'str'):
        #         pass

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
        # self.job_file_path = job_file_path

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
        if not any([freq in freq_interval for freq in  self.available_freq_intervals]):
            raise ValueError('freq_interval must contain one of: ' + str(self.available_freq_intervals))

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
        Create requests and stage them in a file to be submitted later. This must be run before the submit_jobs method.

        Parameters
        ----------
        product: str
            The ECMWF product - e.g. reanalysis-era5-land. A list of all available products can be found by calling self.available_products.
        variables: str or list of str
            The variables from the product. A dict of all available variables per product can be found by calling self.available_variables.
        from_date: str or pd.Timestamp
            The start date.
        to_date: str or pd.Timestamp
            The end date.
        freq_interval: pandas frequency string
            The frequency that the data should be chunked. For example, 'Y' will create yearly files.
        product_types: str, list of str, or None
            The product types if the product has them. A dict of all available product types per product can be found by calling self.available_product_types.
        pressure_levels: str, list of str, or None
            The pressure levels if the product has them. A dict of all available pressure levels per product can be found by calling self.available_pressure_levels.
        output_format: str
            Eiter 'netcdf' or 'grib'.
        check_existing_files: bool
            Should the existing files be checked to make sure they don't get submitted again? This should normally be on. Only turn off for testing.

        Returns
        -------
        pathlib.Path
            staged file path
        """
        variables1, product_types1, bbox1, pressure_levels1, dates1, from_date1 = self._input_checks(product, variables, from_date, to_date, bbox, freq_interval, product_types, pressure_levels, output_format)

        # model_type = models.model_types[product]

        existing_job_hashes = utils.check_completed_jobs(self.save_path, self.s3_base_key, self.s3_session_kwargs)

        ## Add requests
        with booklet.open(self.staged_file_path, 'w') as sf:

            for var in variables1:
                dict1 = {'product': product, 'data_format': output_format, 'variable': [var], 'area': bbox1, 'download_format': 'unarchived'}

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

            ## Remove jobs that have already completed and saved
            for job_hash in existing_job_hashes:
                if job_hash in sf:
                    del sf[job_hash]

        return self.staged_file_path


    def read_staged_file(self):
        """
        Return a dict of all the requests that have been staged. The keys are the hex hashes of the requests.
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


    def clear_jobs(self, job_status=['failed'], remove_local=False):
        """
        Remove jobs on the server and optionally on the local files.

        Parameters
        ----------
        job_status: bool, str, or list of str
            The job statuses that should be removed. If True, then remove everything.
        remove_local: bool
            Should the jobs be removed from the local staged file in addition to the server?

        Returns
        -------
        set of the removed job ids
        """
        if isinstance(job_status, str):
            job_status = [job_status]
        elif isinstance(job_status, bool):
            if job_status:
                job_status = utils.all_statuses
            else:
                raise ValueError('If job_status is a bool, it must be True.')
        elif not isinstance(job_status, (list, tuple, set)):
            raise TypeError('job_status must be iterable or bool.')

        jobs_list = self._get_jobs_list()

        http_session = utils.session()

        remove_job_ids = set()
        with booklet.open(self.staged_file_path, 'w') as sf:
            for job_dict in jobs_list:
                status = job_dict['status']

                if status in job_status:
                    job_id = job_dict['jobID']
                    url = utils.job_delete_url.format(url_endpoint=self.url_endpoint, job_id=job_id)
                    resp = http_session.request('delete', url, headers=self.headers)
                    if resp.status // 100 != 2:
                        raise urllib3.exceptions.HTTPError(resp.json())

                    remove_job_ids.add(job_id)

                    ## Remove job request in staged file
                    if remove_local:
                        job_hash = job_dict['job_hash']
                        if job_hash in sf:
                            del sf[job_hash]

                    sleep(1) # Don't hit the API too fast

        return remove_job_ids


    def submit_jobs(self, n_jobs_queued=15):
        """
        Submit jobs to the server from the requests in the staged file. It will only submit the the value given by the n_jobs_queued parameter.

        Parameters
        ----------
        n_jobs_queued: int
            The max number of jobs to have in the queue on the server.

        Returns
        -------
        set of the job hashes
        """
        jobs = self.get_jobs()

        queued_job_hashes = set()
        for job in jobs:
            if job.status == 'accepted':
                queued_job_hashes.add(job.job_hash)

        existing_job_hashes = utils.check_completed_jobs(self.save_path, self.s3_base_key, self.s3_session_kwargs)

        if len(queued_job_hashes) < n_jobs_queued:
            # print(f'-- {extra_n_queued} jobs will be submitted')

            http_session = utils.session()

            submitted_jobs = set()
            with booklet.open(self.staged_file_path, 'r') as sf:
                # with booklet.open(self.job_file_path, 'w') as jf:
                #     for job_id, jf_job_hash in jf.items():
                #         job_hashes.add(jf_job_hash)

                for job_hash, request_bytes in sf.items():
                    if len(queued_job_hashes) == n_jobs_queued:
                        break

                    if job_hash not in existing_job_hashes or job_hash not in queued_job_hashes:
                        # request_model = models.loads(request_bytes)
                        request_dict = msgspec.json.decode(request_bytes)
                        # model_type = request_model.__class__.__name__
                        product = request_dict['product']
                        request_url = utils.request_url.format(url_endpoint=self.url_endpoint, product=product)

                        # request_dict = msgspec.to_builtins(request_model)
                        request_dict['job_hash'] = job_hash

                        resp = http_session.request('post', request_url, json={'inputs': request_dict}, headers=self.headers)
                        resp_dict = resp.json()
                        if resp.status // 100 != 2:
                            print(resp_dict)
                        else:
                            # job_id = resp_dict['jobID']
                            # jf[job_id] = job_hash
                            queued_job_hashes.add(job_hash)
                            submitted_jobs.add(job_hash)

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
        Get a dict of the jobs on the server that are also in the jobs file. The keys are the job hashes.

        Returns
        -------
        list of Jobs
        """
        jobs_list = self._get_jobs_list()
        jobs = []

        for job_dict in jobs_list:
            # if job_dict['status'] == 'successful':
            #     d
            # job_hash = job_dict['job_hash']
            job = Job(job_dict, self.url_endpoint, self.headers, self.save_path, self.staged_file_path, self.s3_session_kwargs, self.s3_base_key)
            jobs.append(job)

        return jobs


    def run_jobs(self, n_jobs_queued=15):
        """
        An automated process to submit jobs, wait for them to be completed, download completed jobs, and resubmit more jobs. This continues until all of the requests in the staged file are processed.

        Parameters
        ----------
        n_jobs_queued: int
            The max number of jobs to have in the queue on the server.

        Returns
        -------
        int of the number of completed jobs
        """
        n_completed = 0
        while True:
            _ = self.submit_jobs(n_jobs_queued=n_jobs_queued)
            sleep(4)
            try:
                jobs = self.get_jobs()
            except urllib3.exceptions.HTTPError as error:
                print('-- get_jobs failed with the following exception:')
                print(error)
                jobs = []

            if len(jobs) == 0:
                break

            ## If any are successful, then download otherwise delete and try again later
            for job in jobs:
                if job.status == 'successful':
                    if job.error:
                        print('-- Job status is successful, but there are no results:')
                        print(job.error)
                        job.delete(False)
                    else:
                        results_path = job.download_results()
                        print(f'-- {job.file_name} completed')
                        n_completed += 1
                elif job.status == 'failed':
                    job.delete(False)
                    print('-- Job failed with the error:')
                    print(job.error)

            sleep(90)

        return n_completed


class Job:
    """

    """
    def __init__(self, job_dict, url_endpoint, headers, save_path, staged_file_path, s3_session_kwargs, s3_base_key):
        """

        """
        self.s3_base_key = s3_base_key
        self.s3_session_kwargs = s3_session_kwargs
        self._job_hash = None
        self._file_name = None
        self.save_path = save_path
        self.staged_file_path = staged_file_path
        # self.job_file_path = job_file_path
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


    def __repr__(self):
        """

        """
        return f"""
        product:  {self.product}
        job_id:   {self.job_id}
        status:   {self.status}
        created:  {self.created}
        """


    @property
    def job_hash(self):
        """

        """
        if self._job_hash is None:
            self.update()

        return self._job_hash


    @property
    def file_name(self):
        """

        """
        if self._file_name is None:
            self.update()

        return self._file_name


    def update(self):
        """
        Update the data of a job from the server.
        """
        if self.status == 'dismissed':
            raise ValueError('Job has been deleted.')

        if self._job_hash is None:
            req_bool = 'true'
        else:
            req_bool = 'false'

        http_session = utils.session()
        url = utils.job_status_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id, req_bool=req_bool)
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
                # if self.status in ('successful', 'failed'):
                #     with booklet.open(self.job_file_path, 'w') as f:
                #         del f[self.job_id]

        if req_bool == 'true':
            request_dict = job_dict['metadata']['request']['ids']
            self._job_hash = request_dict['job_hash']
            # request_bytes = utils.get_value(self.staged_file_path, self._job_hash)
            # request_model = models.loads(request_bytes)

            file_name = utils.make_file_name(request_dict, self._job_hash, self.product)
            self._file_name = file_name


    def delete(self, remove_local=True):
        """
        Delete the job from the server and locally.

        Parameters
        ----------
        remove_local: bool
            Should the job be removed from the local staged file in addition to the server?
        """
        http_session = utils.session()
        url = utils.job_delete_url.format(url_endpoint=self.url_endpoint, job_id=self.job_id)
        resp = http_session.request('delete', url, headers=self.headers)
        if resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(resp.json())

        self.status = 'dismissed'

        ## Remove from staged file
        if remove_local:
            with booklet.open(self.staged_file_path, 'w') as sf:
                if self.job_hash in sf:
                    del sf[self.job_hash]


    def _download_results_local(self, chunk_size=2**21):
        """

        """
        http_session = utils.session()
        download_url = self.results['href']
        resp = http_session.request('get', download_url, preload_content=False)
        if resp.status // 100 != 2:
            raise urllib3.exceptions.HTTPError(resp.json())

        file_path = self.save_path.joinpath(self.file_name)
        # start = time()
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(resp, f, chunk_size)
        # end = time()
        # print(end - start)

        resp.release_conn()

        return file_path


    def _download_results_s3(self, chunk_size=2**21):
        """

        """
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

        return key_name


    def download_results(self, chunk_size=2**21, delete_job=True):
        """
        Download a completed job. If the S3 parameters were assigned at the Manager init, then it will upload the file to S3.

        Parameters
        ----------
        chunk_size: int
            The read/write chunk size in bytes
        delete_job: bool
            Should the job be deleted after it successfully downloads? This should only be changed for testing purposes.

        Returns
        -------
        pathlib.Path to the file or the S3 object key
        """
        if self.results is None:
            raise ValueError('No results to download.')

        if self.s3_session_kwargs is None:
            path = self._download_results_local(chunk_size)
        else:
            path = self._download_results_s3(chunk_size)

        ## Remove from server
        if delete_job:
            self.delete()

        return path





























































































