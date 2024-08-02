import logging

from pymemcache.client.base import Client
from pymemcache.client.retrying import RetryingClient


def get_base_client(host, port):
    return Client((host, port), connect_timeout=0.05, timeout=0.05)


class Store:
    def __init__(self, host='localhost', port=11211):
        self._cache_client = RetryingClient(
            get_base_client(host, port),
            attempts=2,
            retry_delay=0.05
        )
        self._db_client = RetryingClient(
            get_base_client(host, port),
            attempts=3,
            retry_delay=0.1
        )

    def cache_get(self, key):
        try:
            res = self._cache_client.get(key)
            return res
        except Exception as ex:
            logging.error(f'Error while getting value from cache by key {key}: {ex}')

    def cache_set(self, key, value, expire=60):
        try:
            self._cache_client.set(key, value, expire)
        except Exception as ex:
            logging.error(f'Error while setting value {value} by key {key}: {ex}')

    def get(self, key):
        res = self.cache_get(key)
        if res is None:
            try:
                res = self._db_client.get(key)
            except Exception as ex:
                logging.error(f'Error while getting value from storage by key {key}: {ex}')
                raise MemoryError(ex)
        return res

    def set(self, key, value):
        try:
            self._db_client.set(key, value)
        except Exception as ex:
            logging.error(f'Error while setting value {value} by key {key}: {ex}')
