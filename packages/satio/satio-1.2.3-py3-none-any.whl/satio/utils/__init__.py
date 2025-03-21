import argparse
import concurrent.futures
import json
import multiprocessing
import os
import random
import re
import signal
import string
import sys
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from threading import Timer

import geopandas as gpd
import numpy as np
import psutil
import rasterio
import rasterio.features
import skimage
from loguru import logger
from rasterio.crs import CRS
from rasterio.profiles import Profile
from shapely.geometry import Polygon
from skimage.morphology import binary_erosion
from tqdm.auto import tqdm


class BackgroundTask(ABC):

    def __init__(self,
                 interval):

        self.interval = interval
        self.is_running = False
        self._timer = None

    def _run(self):
        self.is_running = False
        self.start()
        self.task()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self.is_running:
            self._timer.cancel()
            self.is_running = False

    @abstractmethod
    def task(self):
        ...


def _spark_parallelize(sc,
                       func,
                       iterable,
                       num_slices=None,
                       collect=True):
    """
    Run a spark for each safely with logging and exitlogs report if options
    are provided.
    """
    if num_slices is None:
        num_slices = len(iterable)

    if num_slices == 0:
        logger.warning("Nothing to process")
        return None

    try:

        logger.info(f"Starting parallelization of {len(iterable)} tasks.")

        if collect:
            rdd = sc.parallelize(iterable, num_slices).map(func).collect()
        else:
            rdd = sc.parallelize(iterable, num_slices).foreach(func)  # None

        logger.success("Spark processing completed.")

        return rdd

    except Exception as e:
        e_msg = str(e)
        if len(e_msg) > 4096:
            # when using telegram this causes an error because text is too long
            # so this prints the full error to the MEP logs
            print(e_msg)
            e_msg = e_msg[:4096]
        logger.error(f"ERROR - Task interrupted:\n{e}")
        # raise e # causes threadlock
        return e

    finally:

        sc.stop()


def spark_foreach(sc,
                  func,
                  iterable,
                  num_slices=None):
    return _spark_parallelize(sc,
                              func,
                              iterable,
                              num_slices=num_slices,
                              collect=False)


def spark_collect(sc,
                  func,
                  iterable,
                  num_slices=None):
    return _spark_parallelize(sc,
                              func,
                              iterable,
                              num_slices=num_slices,
                              collect=True)


def spark_context(local=False, threads='*', spark_version=None):
    """
    Returns SparkContext for local run.
    if local is True, conf is ignored.

    Customized for VITO MEP
    """
    if spark_version is None:
        spark_version = 2 if sys.version_info.minor < 8 else 3
    sv = spark_version

    spark_home = {2: '/usr/hdp/current/spark2-client',
                  3: '/opt/spark3_0_0'}

    env_vars = {'SPARK_MAJOR_VERSION': str(sv),
                'SPARK_HOME': spark_home[sv]}

    py4j_v = {2: 'py4j-0.10.7', 3: 'py4j-0.10.8.1'}

    spark_py_path = [f'{spark_home[sv]}/python',
                     f'{spark_home[sv]}/python/lib/{py4j_v[sv]}-src.zip']

    for k, v in env_vars.items():
        logger.info(f"Setting env var: {k}={v}")
        os.environ[k] = v

    logger.info(f"Prepending {spark_py_path} to PYTHONPATH")
    sys.path = spark_py_path + sys.path

    import py4j
    logger.info(f"py4j: {py4j.__file__}")

    import pyspark
    logger.info(f"pyspark: {pyspark.__file__}")

    import cloudpickle
    import pyspark.serializers
    from pyspark import SparkConf, SparkContext
    pyspark.serializers.cloudpickle = cloudpickle

    if local:
        logger.info(f"Setting env var: PYSPARK_PYTHON={sys.executable}")
        os.environ['PYSPARK_PYTHON'] = sys.executable

        conf = SparkConf()
        conf.setMaster(f'local[{threads}]')
        conf.set("spark.driver.bindAddress", "127.0.0.1")

        sc = SparkContext(conf=conf)
    else:
        sc = SparkContext()

    return sc


def get_local_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', action='store_true')
    return parser


def get_telegram_handler(config_filename, chat_id=None):

    with open(config_filename, 'r') as f:
        config = json.load(f)

    TELEGRAM_TOKEN = config['telegram'].get('token')

    if chat_id is None:
        TELEGRAM_CHAT_ID = config['telegram'].get('chat_id')
    else:
        TELEGRAM_CHAT_ID = chat_id

    # Add telegram sink for loguru notifications
    if (TELEGRAM_TOKEN is None) | (TELEGRAM_CHAT_ID is None):
        logger.warning("Telegram notifications cannot be sent. "
                       "TELEGRAM_TOKEN and/or TELEGRAM_CHAT_ID chat_id "
                       "variables not set.")
    else:
        params = dict(token=TELEGRAM_TOKEN, chat_id=TELEGRAM_CHAT_ID)
        from notifiers.logging import NotificationHandler
        telegram_handler = NotificationHandler("telegram", defaults=params)
        return telegram_handler


def random_string(n=8):
    x = ''.join(random.choice(string.ascii_uppercase +
                              string.ascii_lowercase +
                              string.digits) for _ in range(n))
    return x


def _glob_match(filename, pattern):
    if re.match(pattern, filename):
        return True
    else:
        return False


def iglob_subfolder(path, pattern):
    """
    Generator that finds all subfolders of path containing the regex `pattern`
    """
    root_dir, folders, files = next(os.walk(path))

    for d in folders:
        new_path = os.path.join(root_dir, d)
        if len(re.findall(pattern, new_path)):
            yield new_path
        else:
            yield from iglob_subfolder(new_path, pattern)


def glob_subfolder(path, pattern, threads=50):
    """
    Return all subfolders of path containing the regex `pattern`
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        folders = list(
            ex.map(lambda x: x, iglob_subfolder(path, pattern)))
    # return [f for f in iglob_subfolder(path, pattern)]
    return folders


def iglob_files(path, pattern=None):
    """
    Generator that finds all subfolders of path containing the regex `pattern`
    """
    root_dir, folders, files = next(os.walk(path))

    for f in files:

        if (pattern is None) or len(re.findall(pattern, f)):
            file_path = os.path.join(root_dir, f)
            yield file_path

    for d in folders:
        new_path = os.path.join(root_dir, d)
        yield from iglob_files(new_path, pattern)


def glob_files(path, pattern=None, threads=50):
    """
    Return all files within path and subdirs containing the regex `pattern`
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        files = list(
            ex.map(lambda x: x, iglob_files(path, pattern)))

    return files


def glob_level_subfolders_sequential(*folders, level=1):
    """
    Return subfolders at given level below the given folders
    """
    current_subs = []
    for f in folders:
        current_subs += [os.path.join(f, sub)
                         for sub in os.walk(f).__next__()[1]]

    level -= 1

    if level == 0:

        return current_subs

    else:

        return glob_level_subfolders_sequential(*current_subs, level=level)


def _glob_subf(folder):
    root, folders, _ = os.walk(folder).__next__()
    return [os.path.join(root, f) for f in folders]


def glob_level_subfolders(folder, level=1, max_workers=20):

    if level < 1:
        raise ValueError('`level` should be greater than 0')

    subfolders = _glob_subf(folder)
    level -= 1

    while level:
        results = run_parallel(_glob_subf,
                               subfolders,
                               max_workers=max_workers,
                               progressbar=False)
        subfolders = [f for r in results for f in r]
        level -= 1

    return subfolders


class DefaultGeoArrayProfile(Profile):
    """Tiled, band-interleaved, LZW-compressed, 8-bit GTiff."""

    defaults = {
        'driver': 'GTiff',
        'interleave': 'band',
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256,
        'compress': 'lzw',
        'dtype': rasterio.float32
    }


def get_profile(arr, bounds, crs):
    base_profile = DefaultGeoArrayProfile()
    shape = arr.shape
    base_profile.update(transform=rasterio.transform.from_bounds(
        *bounds, *shape[-2:]),
        width=shape[2],
        height=shape[1],
        blockxsize=256 if 256 < shape[2] else shape[2],
        blockysize=256 if 256 < shape[1] else shape[1],
        dtype=arr.dtype,
        crs=crs,
        count=shape[0])
    return base_profile


def run_parallel(f,
                 my_iter,
                 max_workers=50,
                 progressbar=True,
                 use_process_pool=False):

    if max_workers == 1:
        # Run tasks sequentially without parallelization
        if progressbar:
            results = [f(item) for item in tqdm(my_iter, total=len(my_iter))]
        else:
            results = [f(item) for item in my_iter]
    else:
        if use_process_pool:
            Pool = concurrent.futures.ProcessPoolExecutor
        else:
            Pool = concurrent.futures.ThreadPoolExecutor

        with Pool(max_workers=max_workers) as ex:
            if progressbar:
                results = list(tqdm(ex.map(f, my_iter), total=len(my_iter)))
            else:
                results = list(ex.map(f, my_iter))
    return results


parallelize = run_parallel


def memory_info():

    mem = psutil.virtual_memory()
    total, used, avail, perc = [mem.total / 1e9,
                                mem.used / 1e9,
                                mem.available / 1e9,
                                mem.percent]
    logger.info(f"Memory:\nTotal\t\t{total:.2f} GB"
                f"\nUsed\t\t{used:.2f} GB"
                f"\nAvail.\t\t{avail:.2f} GB"
                f"\nUsed%\t\t{perc:.1f}%")


def rasterize(gdf,
              bounds,
              epsg,
              resolution=10,
              value_column='Index',
              fill_value=np.nan,
              dtype=np.float32):
    """
    Rasterize a GeoDataFrame to a raster, by giving the bounds
    and epsg of the area to rasterize.
    `value_column` is the column to be used to fill the pixel values
    of each geometry. If none is provided, the index value of the
    geometry will be used.
    """
    out_shape = ((bounds[3] - bounds[1]) // resolution,
                 (bounds[2] - bounds[0]) // resolution)
    out_shape = list(map(int, out_shape))

    gs = gpd.GeoSeries(Polygon.from_bounds(*bounds),
                       crs=CRS.from_epsg(epsg)).to_crs(gdf.crs)
    geom = gs.geometry.values[0]

    geom_rows = gdf[gdf.intersects(geom)].copy()

    if geom_rows.shape[0] == 0:
        # empty gdf
        return np.ones(out_shape, dtype=dtype) * fill_value

    geom_buff = geom.buffer(0.01)
    geom_rows['inter_geometry'] = geom_rows.intersection(geom_buff)

    shapes = [(row.__getattribute__('inter_geometry'),
               row.__getattribute__(value_column)) for row
              in geom_rows.set_geometry('inter_geometry')
              .to_crs(epsg=epsg).itertuples()]

    transform = rasterio.transform.from_bounds(*bounds, *out_shape[::-1])
    try:
        raster = rasterio.features.rasterize(shapes,
                                             out_shape,
                                             fill=fill_value,
                                             transform=transform,
                                             dtype=dtype)
    except ValueError:
        # logger.warning(e)
        raster = np.ones(out_shape, dtype=dtype) * fill_value

    return raster


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def dem_attrs(dem_arr, attributes=['slope_riserun', 'aspect']):
    import richdem as rd
    rda = rd.rdarray(dem_arr, no_data=-9999)
    with HiddenPrints():
        attrs = [rd.TerrainAttribute(rda, attrib=attr) for attr in attributes]
    return attrs


def merge_csv_files(csv_files, merged_csv):

    with merged_csv.open("a") as f:
        for i, c in tqdm(enumerate(csv_files),
                         total=len(csv_files)):
            with Path(c).open() as csv:
                if i != 0:
                    csv.__next__()
                for line in csv:
                    f.write(line)


def merge_csv_files2(csv_files, output_fn):
    """
    Merge list of csv files in single CSV file without loading them all
    in memory
    """
    import shutil

    with open(output_fn, 'wb') as outfile:
        for i, fname in enumerate(tqdm(csv_files, total=len(csv_files))):
            with open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline()  # Throw away header except first file
                # Block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)


def merge_csv_folder(csv_folder, merged_csv):
    csv_folder = Path(csv_folder)
    csv_files = list(csv_folder.glob('**/*.csv'))
    merge_csv_files(csv_files, merged_csv)


class TaskTimerRunningError(Exception):
    ...


class TaskTimer:

    def __init__(self, task_name, unit='minutes'):
        self.name = task_name
        self._total = 0

        self._running = False
        self._start = None

        self._unit = unit

        self._scaling = {'hours': 3600,
                         'minutes': 60,
                         'seconds': 1}.get(unit)

        if self._scaling is None:
            raise ValueError(f'Unknown unit `{unit}`')

    @ property
    def _now(self):
        return time.time()

    def start(self):
        if self._running:
            pass
            # raise TaskTimerRunningError(
            #     'TaskTimer is running, should be stopped before starting')
        self._start = self._now
        self._running = True

    def stop(self):
        if not self._running:
            pass
            # raise TaskTimerRunningError(
            #     'TaskTimer isn't running, should be started before stopping')
        self._total += self._now - self._start
        self._running = False

    @ property
    def _msg(self):
        return 'running for' if self._running else 'took'

    @ property
    def total(self):
        if self._running:
            total = (self._now - self._start) / self._scaling
        else:
            total = self._total / self._scaling

        return total

    def log(self, level='INFO'):
        logger.log(level,
                   f"{self.name} {self._msg} {self.total:.2f} {self._unit}")

    def reset(self):
        self._start = None
        self._running = False
        self._total = 0


# labels arr stats

def _is_edge_pixel(arr: np.ndarray) -> np.ndarray:
    """
    Returns a bool array with pixels True for pixels
    on the edges of the binary input array
    """
    inner = binary_erosion(arr)
    edges = arr ^ inner
    return edges


def is_edge_pixel(lab: np.ndarray) -> np.ndarray:
    """
    Returns bool array with pixels True for pixels
    on the edges of the input array
    """
    lab_vals = [v for v in np.unique(lab) if v != 0]
    edges = np.zeros(lab.shape)
    for v in lab_vals:
        arr = lab == v
        edges += _is_edge_pixel(arr)

    return edges > 0


def count_neighbors(label: np.ndarray) -> np.ndarray:
    """
    Returns a raster where each pixel value corresponds to the number of
    neighboring pixels with the same integer value
    """
    neighb = np.zeros(label.shape)
    regions = skimage.morphology.label(label)
    for v in np.unique(regions):
        neighb[regions == v] = (regions == v).sum()
    return neighb - 1


class DockerMemoryLogger:

    def __init__(self,
                 filename,
                 container_name,
                 interval=1):
        import docker

        self.interval = interval
        self.client = docker.from_env()
        self.client_lowlevel = docker.APIClient(
            base_url='unix://var/run/docker.sock')
        self.container_name = container_name
        self.filename = filename
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._run, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.thread.join()

    def _run(self):
        """ Method that runs forever """
        with open(self.filename, 'w') as f:
            f.write('timestamp,memory,max\n')
            while self.container_running():
                timestamp, usage, max_usage = self.memory_usage()
                if timestamp is not None:
                    f.write(f"{timestamp},{usage},{max_usage}\n")
                    f.flush()
                time.sleep(self.interval)

    def memory_usage(self):

        try:
            stats = self.client_lowlevel.stats(
                container=self.container_name, decode=True).__next__()

            timestamp = stats['read']
            usage = stats['memory_stats']['usage'] / 1e9
            max_usage = stats['memory_stats']['max_usage'] / 1e9

            return timestamp, usage, max_usage

        except Exception as e:
            logger.error(e)
            return None, None, None

    def container_running(self):
        if self.container_name in [c.name for c in
                                   self.client.containers.list()]:
            return True
        else:
            return False

    def memlog(self):
        while self.container_running():
            timestamp, usage, max_usage = self.memory_usage()
            print(f"{timestamp},{usage},{max_usage}")
            time.sleep(self.interval)


def get_random_colors_cmap():
    import matplotlib.pyplot as plt
    vals = np.linspace(0, 1, 256)
    np.random.shuffle(vals)
    cmap = plt.cm.colors.ListedColormap(plt.cm.jet(vals))
    return cmap


def remap_array(arr, mapping: dict = None):
    """
    Remap array values based on mapping dict
    """
    new_arr = arr.copy()
    for k, v in mapping.items():
        new_arr[arr == k] = v

    return new_arr


class TimeoutError(Exception):
    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


# -------------------------------------------------
# From: https://github.com/pnpnpn/timeout-decorator/
# -------------------------------------------------

def _raise_exception(exception, exception_message):
    """ This function checks if a exception message is given.
    If there is no exception message, the default behaviour is maintained.
    If there is an exception message, the message is passed to the
    exception with the 'value' keyword.
    """
    if exception_message is None:
        raise exception()
    else:
        raise exception(exception_message)


def timeout(seconds=None, use_signals=True, timeout_exception=TimeoutError,
            exception_message=None):
    """Add a timeout parameter to a function and return it.
    :param seconds: optional time limit in seconds or fractions of a
    second. If None is passed, no timeout is applied.
        This adds some flexibility to the usage: you can disable timing
        out depending on the settings.
    :type seconds: float
    :param use_signals: flag indicating whether signals should be used
    for timing function out or the multiprocessing
        When using multiprocessing, timeout granularity is limited to
        10ths of a second.
    :type use_signals: bool
    :raises: TimeoutError if time limit is reached
    It is illegal to pass anything other than a function as the first
    parameter. The function is wrapped and returned to the caller.
    """
    from functools import wraps

    def decorate(function):

        if use_signals:
            def handler(signum, frame):
                _raise_exception(timeout_exception, exception_message)

            @wraps(function)
            def new_function(*args, **kwargs):
                new_seconds = kwargs.pop('timeout', seconds)
                if new_seconds:
                    old = signal.signal(signal.SIGALRM, handler)
                    signal.setitimer(signal.ITIMER_REAL, new_seconds)

                if not seconds:
                    return function(*args, **kwargs)

                try:
                    return function(*args, **kwargs)
                finally:
                    if new_seconds:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        signal.signal(signal.SIGALRM, old)
            return new_function
        else:
            @wraps(function)
            def new_function(*args, **kwargs):
                timeout_wrapper = _Timeout(function, timeout_exception,
                                           exception_message, seconds)
                return timeout_wrapper(*args, **kwargs)
            return new_function

    return decorate


def _target(queue, function, *args, **kwargs):
    """Run a function with arguments and return output via a queue.
    This is a helper function for the Process created in _Timeout. It runs
    the function with positional arguments and keyword arguments and then
    returns the function's output by way of a queue. If an exception gets
    raised, it is returned to _Timeout to be raised by the value property.
    """
    try:
        queue.put((True, function(*args, **kwargs)))
    except Exception:
        queue.put((False, sys.exc_info()[1]))


class _Timeout(object):

    """Wrap a function and add a timeout (limit) attribute to it.
    Instances of this class are automatically generated by the add_timeout
    function defined above. Wrapping a function allows asynchronous calls
    to be made and termination of execution after a timeout has passed.
    """

    def __init__(self, function, timeout_exception, exception_message, limit):
        """Initialize instance in preparation for being called."""
        self.__limit = limit
        self.__function = function
        self.__timeout_exception = timeout_exception
        self.__exception_message = exception_message
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.__timeout = time.time()
        self.__process = multiprocessing.Process()
        self.__queue = multiprocessing.Queue()

    def __call__(self, *args, **kwargs):
        """Execute the embedded function object asynchronously.
        The function given to the constructor is transparently called and
        requires that "ready" be intermittently polled. If and when it is
        True, the "value" property may then be checked for returned data.
        """
        self.__limit = kwargs.pop('timeout', self.__limit)
        self.__queue = multiprocessing.Queue(1)
        args = (self.__queue, self.__function) + args
        self.__process = multiprocessing.Process(target=_target,
                                                 args=args,
                                                 kwargs=kwargs)
        self.__process.daemon = True
        self.__process.start()
        if self.__limit is not None:
            self.__timeout = self.__limit + time.time()
        while not self.ready:
            time.sleep(0.01)
        return self.value

    def cancel(self):
        """Terminate any possible execution of the embedded function."""
        if self.__process.is_alive():
            self.__process.terminate()

        _raise_exception(self.__timeout_exception, self.__exception_message)

    @property
    def ready(self):
        """Read-only property indicating status of "value" property."""
        if self.__limit and self.__timeout < time.time():
            self.cancel()
        return self.__queue.full() and not self.__queue.empty()

    @property
    def value(self):
        """Read-only property containing data returned from function."""
        if self.ready is True:
            flag, load = self.__queue.get()
            if flag:
                return load
            raise load
