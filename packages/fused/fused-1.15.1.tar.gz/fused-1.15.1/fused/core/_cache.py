from __future__ import annotations

import base64
import functools
import hashlib
import inspect
import os
import pickle
import re
import shutil
import subprocess
import time
import types
from dataclasses import dataclass, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Awaitable, Callable, Optional, TypeVar
from uuid import uuid4

from loguru import logger

from fused._environment import is_pyodide
from fused._options import options as OPTIONS

# Note: The entirety of this file, except with __future__ import, comes from job2
DEFAULT_CACHE_MAX_AGE = "12h"


@dataclass
class CacheLogEntry:
    expiration: datetime
    uuid: str
    status: str

    # TODO: Make class responsible for serialization to consolidate logic
    @classmethod
    def byte_length(cls):
        ex_length = 32  # datetime.isoformat
        uuid = 36  # str(uuid4())
        status = 1  # char
        commas = len(fields(cls)) - 1
        newline = 1
        return ex_length + uuid + status + commas + newline


# TODO: Possibly move all related methods to a class


def _serialize_code(code: types.CodeType) -> bytes:
    func_code_bytes = base64.b64encode(code.co_code)

    # Introduce variable values into hash.
    func_const_values = [
        # Embedded lambdas must be serialized, same as the overall function
        (
            _serialize_code(const)
            if isinstance(const, types.CodeType)
            else str(const).encode("utf-8")
        )
        for const in code.co_consts
    ]
    # Names must be serialized as otherwise referenced names (min vs max) would not
    # affect cache key.
    func_name_values = [name.encode("utf-8") for name in code.co_names]

    return b"".join(
        [
            func_code_bytes,
            *func_const_values,
            *func_name_values,
        ]
    )


def _serialize_function_defaults(func: Callable) -> bytes:
    parts = []

    if func.__defaults__ is not None:
        for d in func.__defaults__:
            parts.append(_hashify(d).encode("utf-8"))

    if func.__kwdefaults__ is not None:
        for key, value in func.__kwdefaults__.items():
            parts.append(f"{key}{_hashify(value)}".encode("utf-8"))

    return b"".join(parts)


def _hashify(func) -> str:
    hash_object = hashlib.sha256()
    try:
        if hasattr(func, "__fused_cached_fn"):
            return _hashify(func.__fused_cached_fn)
        elif callable(func):
            hash_object.update(_serialize_code(func.__code__))
            # Caution! The defaults and args do not go into the same part of the cache key!
            hash_object.update(_serialize_function_defaults(func))
        else:
            hash_object.update(str(func).encode("utf-8"))
        return hash_object.hexdigest()
    except Exception as e:
        logger.warning(f"Error Hashing {e}")
        return ""


def _parse_time_format(t: str | int) -> timedelta:
    if t == 0 or (isinstance(t, str) and t.strip() == "0"):
        return timedelta(0)

    if isinstance(t, int):
        t = f"{t}s"

    quantifier = re.match(r"(\d+)([smhd])$", t.strip().lower())
    if not quantifier:
        raise ValueError(
            f"Invalid time format {t!r}: Use a number followed by one of 's' (seconds), 'm' (minutes), 'h' (hours), or 'd' (days)."
        )
    value, unit = int(quantifier.group(1)), quantifier.group(2)
    if value < 0:
        raise ValueError(f"Time format {t!r} cannot be less than zero")

    delta_map = {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
    }

    return delta_map[unit]


def _format_now_with_delta(delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    return (now + delta).isoformat()


def _write_cache_file(
    func: Callable,
    args: tuple,
    kwargs: dict,
    cache_path: Path,
    uuid: str,
    expires_on: str,
    timeout_delta: timedelta,
):
    logger.debug(f"Caching {func.__qualname__} under {uuid}")
    in_prog_expires = _format_now_with_delta(timeout_delta)
    # Acquire lock and set status to in-progress
    _write_cache_log(cache_path, uuid, in_prog_expires, status="p")
    try:
        data = func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Error running {func.__qualname__}: {e}")
        # Release lock and set status to fail
        _write_cache_log(cache_path, uuid, expires_on, status="f")
        raise

    with open(cache_path / f"{uuid}.pickle", "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Release lock and set status to done
    _write_cache_log(cache_path, uuid, expires_on, status="d")
    return data


async def _write_cache_file_async(
    func: Callable,
    args: tuple,
    kwargs: dict,
    cache_path: Path,
    uuid: str,
    expires_on: str,
    timeout_delta: timedelta,
):
    logger.debug(f"Caching {func.__qualname__} under {uuid}")
    in_prog_expires = _format_now_with_delta(timeout_delta)
    # Acquire lock and set status to in-progress
    _write_cache_log(cache_path, uuid, in_prog_expires, status="p")
    try:
        data = await func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Error running {func.__qualname__}: {e}")
        # Release lock and set status to fail
        _write_cache_log(cache_path, uuid, expires_on, status="f")
        raise

    with open(cache_path / f"{uuid}.pickle", "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Release lock and set status to done
    _write_cache_log(cache_path, uuid, expires_on, status="d")
    return data


def _write_cache_log(cache_path: Path, uuid: str, expires_on: str, status: str):
    log_file = cache_path / "index.log"
    temp_log = cache_path / f"{uuid}.log"
    shutil.copy(log_file, temp_log)
    with open(temp_log, "a") as f:
        f.write(f"{expires_on},{uuid},{status}\n")
    os.rename(temp_log, log_file)
    logger.debug(f"Wrote {uuid} to cache log {log_file} with status {status}")


def _read_cache_log(cache_path: Path) -> CacheLogEntry | None:
    log_file = cache_path / "index.log"
    # Ensure log file exists
    log_file.touch()
    if is_pyodide():
        try:
            with open(log_file, "rb") as logfile:
                logfile.seek(CacheLogEntry.byte_length() * -1, 2)
                recent_cache_entry = logfile.read().strip().decode("utf8")
        except OSError as e:
            # file is empty
            if "invalid argument" in str(e).lower():
                recent_cache_entry = None
            else:
                logger.debug(f"Reading log file failed: {e}")
                raise

    else:
        try:
            # TODO: Replace tail with builtin file reads and update log file to use fixed byte length record sizes
            # Strip to ensure we don't break if an empty line exists
            recent_cache_entry = subprocess.check_output(
                ["tail", "-1", str(log_file)], encoding="utf8"
            ).strip()
        except CalledProcessError as e:
            # Something wrong with the file or executing command
            logger.debug(f"Reading log file failed: {e}")
            raise

    if recent_cache_entry:
        try:
            expiration, uuid, status = (
                d.strip() for d in recent_cache_entry.split(",")
            )
            logger.debug(
                f"Recent cache entry found in {log_file}: {expiration!r}, {uuid!r}, {status!r}"
            )
            return CacheLogEntry(datetime.fromisoformat(expiration), uuid, status)
        except (TypeError, ValueError) as e:
            logger.debug(
                f"Issues with parsing last line in log {e}. Truncating logfile {log_file}"
            )
            # Any issue with parsing the last line. This could mean the file is corrupted, therefore we clear the file.
            with open(log_file, "w") as logfile:
                logfile.truncate()

    return None


def _read_cache_file(cache_path: Path, uuid: str):
    with open(cache_path / f"{uuid}.pickle", "rb") as f:
        data = pickle.load(f)
        return data


def _cache(
    func: Callable,
    *args,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    reset: bool = False,
    **kwargs,
) -> Any:
    """Internal method used by cache decorator to cache a function's pickleable response to a file.

    Args:
        func: The decorated function.
        *args: Positional arguments to the decorated function.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m),
            hours (h), and days (d) (e.g. "48h", "10s", etc.).
        path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time for concurrent calls to wait for the decorated function
            to finish execution and to write the cache file currently being written by another concurrent call.
            Waiting will end before the timeout if a finished cache file is detected after reading the most recent entry
            in the log. Otherwise, after the timeout, it will either find a finished cached file to read, or it will
            write a new one if a cache file has not been recorded in the log.
        **kwargs: Keyword arguments to the decorated function.

    Returns:
        Any: Result from the cached function
    """
    # Calculate expires_on
    max_age_delta = _parse_time_format(cache_max_age)
    timeout_delta = _parse_time_format(concurrent_lock_timeout)

    try:
        path = path.strip("/")
        # TODO: consider udf name in path once available from Fused global context
        path = OPTIONS.cache_directory / path
        # TODO: ignore `_`

        # 1. Hashify function
        id = _hashify(func)

        # 2. Hashify args
        for v in args:
            id += "_" + _hashify(v)

        # 3. Hashify kwargs
        for k in kwargs:
            id += k + _hashify(kwargs[k])

        # 4. Hashify cache_max_age
        id += _hashify(max_age_delta)

        # 5. Hashify composite id
        id = _hashify(id)

        path_dir = path / f"data_{id}"

        path_dir.mkdir(parents=True, exist_ok=True)

        cache_entry = _read_cache_log(path_dir)
        new_cache_uuid = str(uuid4())
        expires_on = _format_now_with_delta(max_age_delta)
        timeout_seconds = timeout_delta.total_seconds()
        if not reset and cache_entry:
            now = datetime.now(timezone.utc)
            wait_time_seconds = 1
            max_retries = timeout_seconds // wait_time_seconds
            retries = 1
            while (
                cache_entry.status == "p"
                and now < cache_entry.expiration
                and retries < max_retries
            ):
                logger.debug(
                    f"Sleeping. Cache entry reporting {cache_entry.status}, {now} < {cache_entry.expiration}, "
                    f"current write might be in progress. Retry [{retries}/{max_retries}]"
                )
                time.sleep(wait_time_seconds)
                cache_entry = _read_cache_log(path_dir)
                retries += 1

            logger.debug(
                f"Detected status is {cache_entry.status} and expiration is {cache_entry.expiration}"
            )
            if cache_entry.status == "d" and now < cache_entry.expiration:
                logger.debug(
                    f"Reading cache for {func.__qualname__} under {cache_entry.uuid}"
                )
                # Cache exists and valid
                return _read_cache_file(path_dir, cache_entry.uuid)
            else:
                return _write_cache_file(
                    func,
                    args,
                    kwargs,
                    path_dir,
                    new_cache_uuid,
                    expires_on,
                    timeout_delta,
                )

        else:
            return _write_cache_file(
                func, args, kwargs, path_dir, new_cache_uuid, expires_on, timeout_delta
            )

    except Exception as e:
        logger.debug(f"Error Caching {e}")
        raise e


async def _cache_async(
    func: Callable,
    *args,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    reset: bool = False,
    **kwargs,
) -> Any:
    """Async internal method used by cache decorator to cache a function's pickleable response to a file.

    Args:
        func: The decorated function.
        *args: Positional arguments to the decorated function.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m),
            hours (h), and days (d) (e.g. "48h", "10s", etc.).
        path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time for concurrent calls to wait for the decorated function
            to finish execution and to write the cache file currently being written by another concurrent call.
            Waiting will end before the timeout if a finished cache file is detected after reading the most recent entry
            in the log. Otherwise, after the timeout, it will either find a finished cached file to read, or it will
            write a new one if a cache file has not been recorded in the log.
        **kwargs: Keyword arguments to the decorated function.

    Returns:
        Any: Result from the cached function
    """
    # Calculate expires_on
    max_age_delta = _parse_time_format(cache_max_age)
    timeout_delta = _parse_time_format(concurrent_lock_timeout)

    try:
        path = path.strip("/")
        # TODO: consider udf name in path once available from Fused global context
        path = OPTIONS.cache_directory / path
        # TODO: ignore `_`

        # 1. Hashify function
        id = _hashify(func)

        # 2. Hashify args
        for v in args:
            id += "_" + _hashify(v)

        # 3. Hashify kwargs
        for k in kwargs:
            id += k + _hashify(kwargs[k])

        # 4. Hashify cache_max_age
        id += _hashify(max_age_delta)

        # 5. Hashify composite id
        id = _hashify(id)

        path_dir = path / f"data_{id}"

        path_dir.mkdir(parents=True, exist_ok=True)

        cache_entry = _read_cache_log(path_dir)
        new_cache_uuid = str(uuid4())
        expires_on = _format_now_with_delta(max_age_delta)
        timeout_seconds = timeout_delta.total_seconds()
        if not reset and cache_entry:
            now = datetime.now(timezone.utc)
            wait_time_seconds = 1
            max_retries = timeout_seconds // wait_time_seconds
            retries = 1
            while (
                cache_entry.status == "p"
                and now < cache_entry.expiration
                and retries < max_retries
            ):
                logger.debug(
                    f"Sleeping. Cache entry reporting {cache_entry.status}, {now} < {cache_entry.expiration}, "
                    f"current write might be in progress. Retry [{retries}/{max_retries}]"
                )
                time.sleep(wait_time_seconds)
                cache_entry = _read_cache_log(path_dir)
                retries += 1

            logger.debug(
                f"Detected status is {cache_entry.status} and expiration is {cache_entry.expiration}"
            )
            if cache_entry.status == "d" and now < cache_entry.expiration:
                logger.debug(
                    f"Reading cache for {func.__qualname__} under {cache_entry.uuid}"
                )
                # Cache exists and valid
                return _read_cache_file(path_dir, cache_entry.uuid)
            else:
                return await _write_cache_file_async(
                    func,
                    args,
                    kwargs,
                    path_dir,
                    new_cache_uuid,
                    expires_on,
                    timeout_delta,
                )

        else:
            return await _write_cache_file_async(
                func, args, kwargs, path_dir, new_cache_uuid, expires_on, timeout_delta
            )

    except Exception as e:
        logger.debug(f"Error Caching {e}")
        raise e


def _cache_internal(func, **decorator_kwargs):
    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper_async(*args, **kwargs):
                # Allow passing cache kwargs through fn kwargs. Depends on all cache kwargs to be specified from cache
                # decorator
                for k in decorator_kwargs:
                    if k in kwargs:
                        decorator_kwargs[k] = kwargs.pop(k)

                return await _cache_async(
                    func,
                    *args,
                    **decorator_kwargs,
                    **kwargs,
                )

            wrapper_async.__fused_cached_fn = func

            return wrapper_async
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Allow passing cache kwargs through fn kwargs. Depends on all cache kwargs to be specified from cache
                # decorator
                for k in decorator_kwargs:
                    if k in kwargs:
                        decorator_kwargs[k] = kwargs.pop(k)

                return _cache(
                    func,
                    *args,
                    **decorator_kwargs,
                    **kwargs,
                )

            wrapper.__fused_cached_fn = func

            return wrapper

    if callable(func):  # w/o args
        return decorator(func)
    else:  # w/ args
        return decorator


def cache(
    func: Optional[Callable[..., Any]] = None,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    reset: bool = False,
) -> Callable[..., Any]:
    """Decorator to cache the return value of a function.

    This function serves as a decorator that can be applied to any function
    to cache its return values. The cache behavior can be customized through
    keyword arguments.

    Args:
        func (Callable, optional): The function to be decorated. If None, this
            returns a partial decorator with the passed keyword arguments.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m), hours (h), and
            days (d) (e.g. "48h", "10s", etc.).
        path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time in seconds for subsequent concurrent calls to wait for a previous
            concurrent call to finish execution and to write the cache file.

    Returns:
        Callable: A decorator that, when applied to a function, caches its
        return values according to the specified keyword arguments.

    Examples:

        Use the `@cache` decorator to cache the return value of a function in a custom path.

        ```py
        @cache(path="/tmp/custom_path/")
        def expensive_function():
            # Function implementation goes here
            return result
        ```

        If the output of a cached function changes, for example if remote data is modified,
        it can be reset by running the function with the `reset` keyword argument. Afterward,
        the argument can be cleared.

        ```py
        @cache(path="/tmp/custom_path/", reset=True)
        def expensive_function():
            # Function implementation goes here
            return result
        ```
    """
    return _cache_internal(
        func=func,
        cache_max_age=cache_max_age,
        path=path,
        concurrent_lock_timeout=concurrent_lock_timeout,
        reset=reset,
    )


T = TypeVar("T")


def cache_call(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Directly calls a function with caching.

    This function directly calls the provided function with the given arguments
    and keyword arguments, caching its return value. The cache used depends on
    the implementation of the `_cache` function.

    Args:
        func (Callable): The function to call and cache its result.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The cached return value of the function.

    Raises:
        Exception: Propagates any exception raised by the function being called
        or the caching mechanism.
    """
    return _cache(func, *args, **kwargs)


async def cache_call_async(
    func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> T:
    """Asynchronously calls a function with caching.

    Similar to `cache_call`, but for asynchronous functions. This function
    awaits the provided async function, caches its return value, and then
    returns it. The specifics of the caching mechanism depend on the
    implementation of `_cache_async`.

    Args:
        func (Callable): The asynchronous function to call and cache its result.
        *args: Positional arguments to pass to the async function.
        **kwargs: Keyword arguments to pass to the async function.

    Returns:
        The cached return value of the async function.

    Raises:
        Exception: Propagates any exception raised by the async function being
        called or the caching mechanism.

    Examples:
        async def fetch_data(param):
            # Async function implementation goes here
            return data

        # Usage
        result = await cache_call_async(fetch_data, 'example_param')
    """
    return await _cache_async(func, *args, **kwargs)
