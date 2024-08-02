import logging
import time
import unittest
from store import Store
from mockcache import Client as MockClient
from unittest.mock import patch


class TestStoreCacheMethods(unittest.TestCase):
    @patch('store.get_base_client', return_value=MockClient())
    def test_cache_get_connected_existed_value(self, mocked):
        store = Store()
        key = 'some_key'
        value = 'some_value'
        store.cache_set(key, value)
        self.assertEqual(store.cache_get(key), value)

    @patch('store.get_base_client', return_value=MockClient())
    def test_cache_set_connected_with_expiration(self, mocked):
        store = Store()
        key = 'some_key'
        value = 'some_value'
        exp_time = 3
        store.cache_set(key, value, exp_time)
        time.sleep(exp_time)
        self.assertIsNone(store.cache_get(key))

    @patch('store.get_base_client', return_value=MockClient())
    def test_cache_get_connected_no_value(self, *mocked):
        store = Store()
        self.assertIsNone(store.cache_get('some_key'))

    def test_cache_get_disconnected(self):
        store = Store(port='8080')
        self.assertIsNone(store.cache_get('some_key'))

    @patch('store.get_base_client', return_value=MockClient())
    @patch('store.Store.cache_get', return_value=1)
    def test_get_connected_cache_hit(self, mocked_cache_get, *mocked):
        store = Store()
        key = 'some_key'
        self.assertEqual(store.get(key), 1)
        mocked_cache_get.assert_called_once_with(key)

    @patch('store.get_base_client', return_value=MockClient())
    @patch('store.Store.cache_get', return_value=None)
    def test_get_connected_cache_miss(self, mocked_cache_get, *mocked):
        store = Store()
        key = 'some_key'
        value = 'some_value'
        store.set(key, value)
        self.assertEqual(store.get(key), value)
        mocked_cache_get.assert_called_once_with(key)

    @patch('store.Store.cache_get', return_value=None)
    def test_get_disconnected(self, mocked_cache_get):
        store = Store(port='8080')
        key = 'some_key'
        with self.assertRaises(MemoryError):
            store.get(key)
        mocked_cache_get.assert_called_once_with(key)


logging.disable(logging.ERROR)
if __name__ == '__main__':
    unittest.main()
