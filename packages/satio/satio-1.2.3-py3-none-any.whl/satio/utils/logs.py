import os
import time
import glob
import functools
import threading
import _thread
import datetime
from pathlib import Path

import pytz
import psutil
from loguru import logger

from satio.utils import BackgroundTask


EXITLOGS_LEVEL = 69
logger.level("EXITLOGS", no=EXITLOGS_LEVEL, color="<magenta>")
logger.__class__.exitlogs = functools.partialmethod(
    logger.__class__.log, "EXITLOGS")


def _loguru_exitlogs_filter(record):
    return record["level"].no == EXITLOGS_LEVEL


def thread_id():
    return threading.current_thread().ident


def exitlogs(logs_folder,
             skip_processed=False,
             verbose=True,
             errors_only=False,
             raise_exceptions=False):
    """
    Decorator that produces a "DONE_{task_id}.log" or "ERROR_{task_id}.log"
    if the function decorated completes or fails with an error.
    """
    def decorator_exitlog(func):

        @functools.wraps(func)
        def wrapper_exitlog(*args, **kwargs):

            if logs_folder is None:
                return func(*args, **kwargs)

            tup = args[0]
            task_id = tup[0]
            if len(tup) != 2:
                raise ValueError("Input should be a tuple '(task_id, row)'")

            folder = Path(logs_folder)
            folder.mkdir(parents=True, exist_ok=True)

            done_log = folder / f'DONE_{task_id}.log'
            error_log = folder / f'ERROR_{task_id}.log'

            if skip_processed:
                if done_log.is_file():
                    if verbose:
                        logger.warning(f"Task {task_id} already processed, "
                                       "skipping...")
                    return None

                if error_log.is_file():
                    os.remove(error_log)

            try:

                start_time = time.time()
                if verbose:
                    logger.info(f"Starting processing of {task_id}.")

                value = func(*args, **kwargs)

                if not errors_only:
                    done_sink = logger.add(
                        done_log,
                        filter=lambda record: record["thread"].id == thread_id())  # NOQA

                processing_time = time.time() - start_time
                if verbose:
                    logger.success(f"Processing of {task_id} completed in "
                                   f"{processing_time / 60:.2f} minutes.")

                if not errors_only:
                    logger.remove(done_sink)  # type: ignore

            except Exception as e:
                err_sink = logger.add(
                    error_log,
                    filter=lambda record: record["thread"].id == thread_id())

                if verbose:
                    logger.exception('Error occurred while processing task '
                                     f"with task id '{task_id}':\n\n{e}")
                logger.remove(err_sink)

                value = None

                if raise_exceptions:
                    raise

            return value

        return wrapper_exitlog
    return decorator_exitlog


def exitlogs_report(folder):
    """
    Globs the folder for .log files and returns a two lists of logs,
    one containing DONE logs and one containing ERROR logs.
    """
    # logs = glob.glob(os.path.join(folder, '**', '*.log'),
    #                  recursive=True)
    logs = glob.iglob(os.path.join(folder, '*.log'))
    done, errors = [], []
    for g in logs:
        if 'DONE' in g:
            done.append(g)
        elif 'ERROR' in g:
            errors.append(g)
        else:
            pass

    return done, errors


class ExitLogsMonitor(BackgroundTask):

    def __init__(self, logs_folder, interval=300,
                 telegram_token=None, telegram_chat_id=None):

        super().__init__(interval)
        self.logs_folder = Path(logs_folder)
        self.done = None
        self.errors = None

        self.done_ids = None
        self.errors_ids = None

        if telegram_token is not None and telegram_chat_id is not None:
            telegram = self._get_telegram_sink(telegram_token,
                                               telegram_chat_id)
            self._sink_id = logger.add(telegram,
                                       level=EXITLOGS_LEVEL)
        else:
            self._sink_id = None

    def stop(self):
        if self._sink_id is not None:
            logger.remove(self._sink_id)
        super().stop()

    def update(self):
        logger.exitlogs(f"Globbing logs in {self.logs_folder}")
        done, errors = exitlogs_report(self.logs_folder)

        self._nd, self._ne = len(done), len(errors)
        self.done = done
        self.errors = errors

        self.done_ids = list(map(self._get_id, self.done))
        self.errors_ids = list(map(self._get_id, self.errors))

    def task(self):

        self.update()

        logger.exitlogs(f"DONE logs: {self._nd}")
        logger.exitlogs(f"ERROR logs: {self._ne}")

    @staticmethod
    def _get_id(log_fname):
        bn = os.path.basename(log_fname).split('.')[0]
        task_id = "_".join(bn.split('_')[1:])
        return task_id

    def read_log(self, task_id):
        logs = self.done + self.errors
        ids = self.done_ids + self.errors_ids

        log = logs[ids.index(task_id)]

        with open(log, 'r') as f:
            text = f.read()

        return text

    @staticmethod
    def _get_telegram_sink(token, chat_id):
        import notifiers

        def telegram_sink(message):
            notifier = notifiers.get_notifier("telegram")
            notifier.notify(message=message, token=token, chat_id=chat_id)

        return telegram_sink

    def filter_done(self, tasks):
        self.task()

        ids = [t[0] for t in tasks]
        ids = list(map(str, ids))
        todo_ids = set(ids) - set(self.done_ids)
        todo_tasks = [t for t in tasks
                      if str(t[0]) in todo_ids]

        return todo_tasks


def proclogs(logs_folder=None, level='INFO'):
    """
    Decorator that adds a task loguru sink to a file
    """
    def decorator_exitlog(func):

        @functools.wraps(func)
        def wrapper_exitlog(*args, **kwargs):

            if logs_folder is None:
                return func(*args, **kwargs)

            tup = args[0]
            task_id = tup[0]
            if len(tup) != 2:
                raise ValueError("Input should be a tuple '(task_id, row)'")

            folder = Path(logs_folder)
            folder.mkdir(parents=True, exist_ok=True)

            log = folder / f'{task_id}_{{time}}.log'
            sink = logger.add(
                log,
                level=level,
                filter=lambda record: record["thread"].id == thread_id())

            value = func(*args, **kwargs)

            logger.remove(sink)

            return value

        return wrapper_exitlog
    return decorator_exitlog


class MemoryLimitError(Exception):
    ...


class LocalMemLoggerDaemon:

    def __init__(self,
                 interval,
                 filename,
                 memory_limit_mb=0,
                 max_spikes_number=0):
        """
        If max_spikes is > 0, memory usage is allowed to be above limit
        for `max_spikes` consecutive intervals.
        """
        self.interval = interval
        self.pid = self.get_pid()
        self.filename = filename
        self.is_running = False

        self._timer = None
        self.max_rss = 0

        self._keeprunning = True

        self._mem_limit = memory_limit_mb
        self._mem_spikes = 0

        self._max_spikes = max_spikes_number
        self._spikes = 0

        self.memory_error = None

    @staticmethod
    def get_pid():
        """ Get the pid from the environment """
        # if "JVM_PID" in os.environ:
        #     # use the JVM pid
        #     pid = int(os.environ["JVM_PID"])
        # else:
        #     # otherwise get the pid of the current python job
        pid = os.getpid()
        return pid

    def start(self):
        self.thread = threading.Thread(target=self._run, args=(),
                                       daemon=True)
        self.thread.start()

    def stop(self):
        self._keeprunning = False

    def _run(self):
        """ Method that runs forever """
        try:
            with open(self.filename, 'w') as f:
                f.write('timestamp,memory,max\n')
                while self._keeprunning:
                    timestamp, usage, max_usage = self.memory_usage()
                    if timestamp is not None:
                        f.write(f"{timestamp},{usage},{max_usage}\n")
                        f.flush()
                    time.sleep(self.interval)

                    if (self._mem_limit > 0) and (usage > self._mem_limit):
                        self._spikes += 1

                        msg = (f"Memory usage of {usage} mb exceeded set limit"
                               f" of {self._mem_limit} mb")

                        if self._spikes > self._max_spikes:
                            self.memory_error = MemoryLimitError(msg)
                            raise MemoryLimitError(msg)
                        else:
                            logger.warning(msg)

                    else:
                        self._spikes = 0  # reset spikes counter

                logger.exitlogs("Memory logging stopped")

        except MemoryLimitError as e:
            logger.error(f"Terminating main process: {e}")
            _thread.interrupt_main()

        except Exception:
            pass

    def memory_usage(self):
        """
        Log memory usage to Kafka topic.
        Uses psutil module to get the memory.
        """
        pid = self.pid
        try:
            # get the parent pid of the JVM pid
            parent = psutil.Process(pid).parent()

            # now get the memory of parent and all children
            rss_mem = parent.memory_info().rss
            for child in parent.children(recursive=True):
                rss_mem += child.memory_info().rss

            rss_mem_mb = int(rss_mem // 1e6)
            timestamp = datetime.datetime.now(tz=pytz.utc).isoformat()

            self.max_rss = max([self.max_rss, rss_mem_mb])

            return timestamp, rss_mem_mb, self.max_rss

        except Exception:
            return None, None, None


class ProcMemLoggerDaemon(LocalMemLoggerDaemon):

    def _run(self):
        """ Method that runs forever """
        try:
            with open(self.filename, 'w') as f:
                f.write('timestamp,memory,max\n')
                while True:
                    timestamp, usage, max_usage = self.memory_usage()
                    if timestamp is not None:
                        f.write(f"{timestamp},{usage},{max_usage}\n")
                        f.flush()
                        logger.info(f"{timestamp},{usage},{max_usage}")
                    time.sleep(self.interval)

        except Exception:
            pass


def memlogs(memlogs_folder=None,
            memlogs_interval=1,
            memory_limit_mb=0,
            max_spikes_number=2):
    """
    Decorator that memory logs csv and .max memory log for each task_id.
    """
    import signal
    import sys

    def decorator_exitlog(func):

        @functools.wraps(func)
        def wrapper_exitlog(*args, **kwargs):

            if memlogs_folder is None:
                return func(*args, **kwargs)

            tup = args[0]
            task_id = tup[0]
            if len(tup) != 2:
                raise ValueError("Input should be a tuple '(task_id, row)'")

            folder = Path(memlogs_folder)
            folder.mkdir(parents=True, exist_ok=True)

            mem_log = folder / f'mem_{task_id}.csv'
            max_log = folder / f'mem_{task_id}.max'

            ml = LocalMemLoggerDaemon(interval=memlogs_interval,
                                      filename=mem_log,
                                      memory_limit_mb=memory_limit_mb,
                                      max_spikes_number=max_spikes_number)
            ml.start()

            # handle termination from child thread when memory usage exceeds
            def signal_handler(sig, frame):
                if ml.memory_error is not None:
                    raise ml.memory_error
                else:
                    raise KeyboardInterrupt

            signal.signal(signal.SIGINT, signal_handler)

            try:
                value = func(*args, **kwargs)

            except Exception as e:
                raise e

            finally:
                ml.stop()  # stop daemon
                max_log.write_text(str(ml.max_rss))

            return value

        return wrapper_exitlog
    return decorator_exitlog


def procmemlogs(memlogs_folder=None,
                memlogs_interval=1):
    """
    WARNING: CAUSES THREADLOCKS. DO NOT USE ON THE CLUSTER or you will freeze
    executors and the app won't progress.

    Decorator that memory logs csv and .max memory log for each task_id.
    """
    def decorator_exitlog(func):

        @functools.wraps(func)
        def wrapper_exitlog(*args, **kwargs):

            if memlogs_folder is None:
                return func(*args, **kwargs)

            tup = args[0]
            task_id = tup[0]
            if len(tup) != 2:
                raise ValueError("Input should be a tuple '(task_id, row)'")

            folder = Path(memlogs_folder)
            folder.mkdir(parents=True, exist_ok=True)

            mem_log = folder / f'mem_{task_id}.csv'
            max_log = folder / f'mem_{task_id}.max'

            level = 'DEBUG'
            loguru_log = folder / f'mem_{task_id}_{{time}}.log'
            sink = logger.add(
                loguru_log,
                level=level,
                filter=lambda record: record["thread"].id == thread_id())

            ml = None

            try:

                ml = ProcMemLoggerDaemon(interval=memlogs_interval,
                                         filename=mem_log)
                ml.start()

                # logger.info(f"Logging memory of {task_id} to {mem_log}.")

                value = func(*args, **kwargs)

            except Exception:
                pass

            finally:
                max_log.write_text(str(ml.max_rss))
                ml.stop()
                value = None

            return value

        return wrapper_exitlog
    return decorator_exitlog
