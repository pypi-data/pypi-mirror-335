import os
import hashlib
import time
import pickle
import sys
import datetime

from copy import copy
from typing import Optional

from .model import models
from .utils import fs

ACCEPTABLE_BACKENDS = ['fs']


def _get_cache_entry(
        backend: str,
        storage: str,
        ttl: int,
        cache_entry_id: str,
) -> Optional[models.CacheEntry]:
    if backend == 'fs':
        filepath = os.path.join(storage, cache_entry_id)
        file_timestamp = fs.get_file_timestamp(filepath) if fs.file_exists(filepath) else None

        if not file_timestamp or (time.time() - file_timestamp > ttl):
            fs.safe_remove_file(filepath)
            return None

        with open(filepath, 'rb') as fp:
            response = pickle.load(fp)
        return models.CacheEntry(
            id=cache_entry_id,
            size=sys.getsizeof(response),
            result=response,
            created_at=datetime.datetime.fromtimestamp(file_timestamp),
        )

    raise NotImplementedError(f'Backend({backend}) is not implemented')


def _create_cache_entry(
        backend: str,
        storage: str,
        cache_entry_id: str,
        response,
) -> models.CacheEntry:
    if backend == 'fs':
        filepath = os.path.join(storage, cache_entry_id)

        with open(filepath, 'wb') as fp:
            pickle.dump(response, fp)
        return models.CacheEntry(
            id=cache_entry_id,
            size=sys.getsizeof(response),
            result=response,
            created_at=datetime.datetime.now(),
        )

    raise NotImplementedError(f'Backend({backend}) is not implemented')


def cache(
        ttl: int = -1,
        backend: str = 'fs',
        storage: Optional[str] = 'cache',
):
    """
    :param ttl: Time-to-live for cache entries
    :param backend: Backend to used for storage. Default: fs (file-system)
    :param storage: Storage to be used. If fs is selected as backend this will be the file-system directory
    :return: Return value of cached method
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            assert (
                    backend in ACCEPTABLE_BACKENDS
            ), f'cache decorator expects one of: {ACCEPTABLE_BACKENDS} as backends'

            caller = f'{function.__module__}.{function.__name__}'
            params = copy(kwargs)
            params['args'] = args

            if backend == 'fs':
                fs.create_directory(storage)

            m = hashlib.md5()
            m.update((caller + str(params)).encode('utf-8'))

            cache_entry_id = m.hexdigest()
            cache_entry = _get_cache_entry(
                backend=backend,
                storage=storage,
                ttl=ttl,
                cache_entry_id=cache_entry_id,
            )

            if not cache_entry:
                response = function(*args, **kwargs)
                cache_entry = _create_cache_entry(
                    backend=backend,
                    storage=storage,
                    cache_entry_id=cache_entry_id,
                    response=response,
                )

            return cache_entry.result

        return wrapper

    return decorator
