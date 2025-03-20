import unittest
from unittest.mock import patch, MagicMock

import pymongo
from drs_id_mongo_publisher.utils.utils_mongo import MongoUtil


class TestMongoUtil(unittest.TestCase):

    @patch('drs_id_mongo_publisher.utils.utils_mongo.EnvDetails')
    @patch('drs_id_mongo_publisher.utils.utils_mongo.pymongo.MongoClient')
    @patch('drs_id_mongo_publisher.utils.utils_mongo.configure_logger')
    def setUp(self, mock_logger, mock_mongo_client, mock_env_details):
        self.mock_env_details = mock_env_details
        self.mock_mongo_client = mock_mongo_client
        self.mock_logger = mock_logger

        self.mock_env_details_instance = MagicMock()
        self.mock_env_details.return_value = self.mock_env_details_instance
        self.mock_env_details_instance.get_mongo_url.return_value = \
            'mongodb://localhost:27017'
        self.mock_env_details_instance.get_mongo_db.return_value = 'test_db'
        self.mock_env_details_instance.get_mongo_collection.return_value = \
            'test_collection'

        self.mock_client_instance = MagicMock()
        self.mock_mongo_client.return_value = self.mock_client_instance
        self.mock_db_instance = MagicMock()
        self.mock_client_instance.__getitem__.return_value = \
            self.mock_db_instance
        self.mock_collection_instance = MagicMock()
        self.mock_db_instance.__getitem__.return_value = \
            self.mock_collection_instance

        self.mongo_util = MongoUtil(env='test_env', dryrun=False)

    def test_insert_record(self):
        record = {'key': 'value'}
        self.mongo_util.insert_record(record)
        self.mock_collection_instance.insert_one.assert_called_once_with(
            record)

    def test_insert_many(self):
        records = [{'key': 'value1'}, {'key': 'value2'}]
        self.mongo_util.insert_many(records)
        self.mock_collection_instance.insert_many.assert_called_once_with(
            records)

    def test_insert_many_bulk_write_error(self):
        records = [{'key': 'value1'}, {'key': 'value2'}]
        self.mock_collection_instance.insert_many.side_effect = \
            pymongo.errors.BulkWriteError({'writeErrors': []})
        with self.assertRaises(pymongo.errors.BulkWriteError):
            self.mongo_util.insert_many(records)

    def test_close_connection(self):
        self.mongo_util.close_connection()
        self.mock_client_instance.close.assert_called_once()

    def test_get_mongo_db(self):
        db = self.mongo_util._get_mongo_db('test_env',
                                           self.mock_client_instance)
        self.assertEqual(db, self.mock_db_instance)

    def test_get_mongo_collection(self):
        collection = self.mongo_util._get_mongo_collection(
            'test_env',
            self.mock_db_instance)
        self.assertEqual(collection, self.mock_collection_instance)


if __name__ == '__main__':
    unittest.main()
