import re
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import boto3
import botocore
import numpy as np
from loguru import logger


class S3BucketReader:
    """
    Helper class to browse AWS S3 buckets using boto3
    """

    def __init__(self,
                 client: boto3.client,
                 bucket,
                 requester_pays=False):

        self.client = client
        self.bucket = bucket
        self._params = dict(Bucket=bucket)
        self._pag = client.get_paginator('list_objects_v2')
        self._requester_pays = requester_pays

        if requester_pays:
            self._params.update(RequestPayer='requester')

    @classmethod
    def from_credentials(cls,
                         aws_access_key_id,
                         aws_secret_access_key,
                         bucket,
                         requester_pays=False,
                         aws_region='eu-central-1',
                         max_pool_connections=100,
                         endpoint_url=None):

        client_config = botocore.config.Config(
            max_pool_connections=max_pool_connections,
        )

        client = boto3.client('s3',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=aws_region,
                              config=client_config,
                              endpoint_url=endpoint_url)

        return cls(client, bucket, requester_pays)

    @property
    def params(self):
        return self._params.copy()

    def read_text(self, key):
        """
        Load a text file from S3
        """
        client = self.client
        params = self.params
        params.update(Key=key)

        fileobj = client.get_object(**params)

        filedata = fileobj['Body'].read()
        return filedata.decode('utf-8')

    def read_json(self, key):
        """
        Load a JSON file from S3
        """
        contents = json.loads(self.read_text(key))
        return contents

    def list_contents(self, prefix='', recursive=False,
                      folders=True, files=True):
        """
        Returns a dictionary of 'folders' and 'files' at the given prefix.
        """
        pag = self._pag
        params = self.params
        params.update(Prefix=prefix)
        if not recursive:
            params.update(Delimiter='/')

        dirs_meta, files_meta = [], []
        for subset in pag.paginate(**params):
            if ('CommonPrefixes' in subset.keys()) and folders:
                dirs_meta.extend(subset.get('CommonPrefixes'))
            if ('Contents' in subset.keys()) and files:
                files_meta.extend(subset.get('Contents'))

        dirs = [d['Prefix'] for d in dirs_meta]
        files = [f['Key'] for f in files_meta]

        contents = {'folders': dirs, 'files': files}

        return contents

    def list_dirs(self, prefix=''):
        return self.list_contents(prefix=prefix,
                                  files=False)['folders']

    def list_files(self, prefix='', recursive=False):
        return self.list_contents(prefix=prefix,
                                  recursive=recursive,
                                  folders=False)['files']

    def download(self, key, filename, verbose=False,
                 overwrite=False):

        if self._requester_pays:
            extra_args = dict(RequestPayer='requester')
        else:
            extra_args = {}

        filename = Path(filename)

        if filename.is_file():
            if verbose:
                logger.info(f"{filename} exists already.")
        else:
            if verbose:
                logger.info(f"Downloading s3://{self.bucket}/{key} "
                            f"to {filename}")
            self.client.download_file(Bucket=self.bucket,
                                      Key=key,
                                      Filename=str(filename),
                                      ExtraArgs=extra_args)

    def download_folder(self,
                        key,
                        output_folder,
                        regex_pattern=None,
                        verbose=False,
                        overwrite=False):

        output_folder = Path(output_folder)
        contents = self.list_contents(key)
        folders, files = contents['folders'], contents['files']

        for file in files:

            if regex_pattern is not None:
                if re.compile(f'{regex_pattern}').search(file) is None:
                    continue

            output_filename = output_folder / Path(file).name
            output_filename.parent.mkdir(parents=True, exist_ok=True)

            self.download(file,
                          output_filename,
                          verbose=verbose,
                          overwrite=overwrite)

        for fold in folders:
            if verbose:
                logger.info(f"Downloading folder: s3://{self.bucket}/{key}")
            self.download_folder(fold,
                                 output_folder / Path(fold).name,
                                 verbose=verbose,
                                 overwrite=overwrite)

    def exists(self, key):
        import botocore

        client = self.client
        params = self.params
        params.update(Key=key)

        try:
            client.head_object(**params)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                return False
            else:
                raise

    def upload(self, fn, key):
        from botocore.exceptions import ClientError
        try:
            logger.debug(f"Uploading {fn} to {key}")
            response = self.client.upload_file(Filename=fn,
                                               Bucket=self.bucket,
                                               Key=key)
        except ClientError as e:
            logger.error(f'Failed to upload: {fn}: {e}')
            raise e
        return True

    def upload_folder(self, folder, folder_key_prefix):
        from satio.utils import iglob_files
        folder = Path(folder).absolute()
        files_gen = iglob_files(folder)
        for fn in files_gen:
            key = str(Path(folder_key_prefix) / Path(fn).relative_to(folder))
            self.upload(fn, key)


class AWSL2ABucket(S3BucketReader):

    def __init__(self, client):
        bucket = 'sentinel-s2-l2a'
        super().__init__(client, bucket, requester_pays=True)

    @classmethod
    def from_credentials(cls,
                         aws_access_key_id,
                         aws_secret_access_key,
                         max_pool_connections=50):

        client_config = botocore.config.Config(
            max_pool_connections=max_pool_connections,
        )

        AWS_REGION = 'eu-central-1'  # L2A bucket location
        client = boto3.client('s3',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=AWS_REGION,
                              config=client_config)
        return cls(client)

    @staticmethod
    def _get_utm_lat_grid(tile):
        utm = tile[:2].lstrip('0')
        lat = tile[2]
        grid = tile[3:]
        return utm, lat, grid

    def get_yearly_products(self, tile, year=2019, max_workers=10):

        utm, lat, grid = self._get_utm_lat_grid(tile)

        months = list(range(1, 13))

        def get_products_days(utm, lat, grid, year, month):
            prefix = f'tiles/{utm}/{lat}/{grid}/{year}/{month}/'
            return self.list_dirs(prefix)

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(lambda x: get_products_days(
                utm, lat, grid, year, x), months)
            products_days = [r for nr in mapper for r in nr]

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(self.list_dirs, products_days)
            products_paths = [r for nr in mapper for r in nr]

        return products_paths

    def _get_tile_products(self, tile,
                           start_date='2019-01-01',
                           end_date='2020-01-01',
                           max_workers=10):

        utm, lat, grid = self._get_utm_lat_grid(tile)

        years_months = self._get_years_months(start_date, end_date)

        def get_products_days(utm, lat, grid, year, month):
            prefix = f'tiles/{utm}/{lat}/{grid}/{year}/{month}/'
            return self.list_dirs(prefix)

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(lambda year_month: get_products_days(
                utm, lat, grid, year_month[0], year_month[1]), years_months)
            products_days = [r for nr in mapper for r in nr]

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            mapper = ex.map(self.list_dirs, products_days)
            products_paths = [r for nr in mapper for r in nr]

        products_paths = list(map(lambda x: f's3://{self.bucket}/' + x,
                                  products_paths))
        return products_paths

    @staticmethod
    def _convert_dates(*dates):
        new_dates = []
        fmt = "%Y-%m-%d"

        for d in dates:
            if isinstance(d, str):
                new_dates.append(datetime.strptime(d, fmt))
            elif isinstance(d, datetime):
                new_dates.append(d)
            else:
                raise ValueError("Type of date not recognized. Should be "
                                 "a string in the format '%Y-%m-%d' or a "
                                 "'datetime.datetime' instance. Instead is: "
                                 f"type({d}): {type(d)}")
        return new_dates

    def _get_years_months(self, start_date, end_date):
        """
        Returns a tuple (year, month) for all the months in the dates interval.
        Dates should be strings with format %Y-%m-%d
        """

        s, e = self._convert_dates(start_date, end_date)

        years = list(range(s.year, e.year + 1))

        start_month = s.month
        end_month = e.month

        year_months = []
        for y in years:

            if len(years) == 1:
                year_months += [(y, m)
                                for m in range(start_month, end_month + 1)]
                return year_months

            if y == years[0]:
                year_months += [(y, m) for m in range(start_month, 13)]

            elif y == years[-1]:
                year_months += [(y, m) for m in range(1, end_month + 1)]

            else:
                year_months += [(y, m) for m in range(1, 13)]

        return year_months

    @staticmethod
    def _get_product_date(x):
        s = x.strip('/').split('/')
        year, month, day = int(s[-4]), int(s[-3]), int(s[-2])
        return datetime(year, month, day)

    def get_tile_products(self,
                          tile,
                          start_date='2019-01-01',
                          end_date='2020-01-01',
                          max_workers=10):

        start_date, end_date = self._convert_dates(start_date, end_date)

        products = self._get_tile_products(tile, start_date, end_date,
                                           max_workers)

        products = np.array(products)
        products_dates = np.array([self._get_product_date(x)
                                   for x in products])

        valid_ids = np.where((products_dates >= start_date) &
                             (products_dates < end_date))[0]

        valid_products = products[valid_ids].tolist()

        return valid_products

    def download_product(self,
                         product_key,
                         download_folder,
                         max_workers=4,
                         verbose=False,
                         overwrite=False):

        r10_files = [f'R10m/B{n:02d}.jp2' for n in [2, 3, 4, 8]]
        r20_files = [f'R20m/B{n:02d}.jp2'
                     for n in [5, 6, 7, 11, 12]] + [f'R20m/SCL.jp2']
        r60_files = [f'R60m/SCL.jp2']

        basenames = r10_files + r20_files + r60_files
        keys = [f'{product_key}/{f}' for f in basenames]

        download_folder = Path(download_folder)
        product_folder = download_folder

        for f in ['R10m', 'R20m', 'R60m']:
            sub_folder = product_folder / f
            sub_folder.mkdir(parents=True, exist_ok=True)

        dst_filenames = [product_folder / b for b in basenames]

        kd_tuples = list(zip(keys, dst_filenames))

        def _download(tup):
            k, d = tup
            self.download(k, d, verbose=verbose, overwrite=overwrite)

        # parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            _ = list(ex.map(_download, kd_tuples))
