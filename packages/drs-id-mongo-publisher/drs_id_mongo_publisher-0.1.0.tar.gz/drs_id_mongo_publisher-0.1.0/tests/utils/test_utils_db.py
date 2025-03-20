import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from drs_id_mongo_publisher.utils.utils_db import DrsDB


class TestDrsDB(unittest.TestCase):

    @patch('drs_id_mongo_publisher.utils.utils_db.load_dotenv')
    @patch('drs_id_mongo_publisher.utils.utils_db.configure_logger')
    @patch('drs_id_mongo_publisher.utils.utils_db.EnvDetails')
    @patch('drs_id_mongo_publisher.utils.utils_db.oracledb.connect')
    def setUp(self, mock_connect,
              mock_env_details,
              mock_logger,
              mock_load_dotenv):
        self.mock_db = MagicMock()
        mock_connect.return_value = self.mock_db
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value = self.mock_cursor
        self.env = 'test_env'

        # Patch the _do_execute method
        self.drs_db = DrsDB(self.env)
        self.patcher = mock.patch.object(self.drs_db, '_do_execute',
                                         return_value=self.mock_cursor)
        self.mock_execute = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_get_obj_details_all(self):
        mock_obj_ids = [1, 2, 3]
        self.drs_db._get_obj_ids_all = MagicMock(
            return_value=iter(mock_obj_ids))
        self.drs_db.get_obj_details_by_obj_ids = MagicMock(
            return_value=[{'OBJ_ID': 1, 'OIS_URN': 'urn:1'},
                          {'OBJ_ID': 2, 'OIS_URN': 'urn:2'},
                          {'OBJ_ID': 3, 'OIS_URN': 'urn:3'}])

        result = self.drs_db.get_obj_details_all()

        self.drs_db._get_obj_ids_all.assert_called_once()

        for r in result:
            self.assertTrue(r['OBJ_ID'] in [1, 2, 3])
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['OBJ_ID'], 1)
        self.assertEqual(result[1]['OBJ_ID'], 2)
        self.assertEqual(result[2]['OBJ_ID'], 3)
        self.assertEqual(result[0]['OIS_URN'], 'urn:1')
        self.assertEqual(result[1]['OIS_URN'], 'urn:2')
        self.assertEqual(result[2]['OIS_URN'], 'urn:3')

    def test_get_obj_details_by_obj_ids(self):
        mock_obj_ids = [1, 2, 3]
        self.mock_cursor.fetchall.side_effect = [
            [(1, 'urn:1'), (2, 'urn:2')],
            [(3, 'urn:3')]]

        result = self.drs_db.get_obj_details_by_obj_ids(iter(mock_obj_ids),
                                                        chunk_size=2)

        expected_query_1 = """
        SELECT do.id as "DRS_OBJECT_ID", do.OIS_URN
        FROM REPOSITORY.DRS_OBJECT do WHERE do.id IN ('1', '2')
        """
        expected_query_2 = """
        SELECT do.id as "DRS_OBJECT_ID", do.OIS_URN
        FROM REPOSITORY.DRS_OBJECT do WHERE do.id IN ('3')
        """
        self.drs_db._do_execute.assert_any_call(expected_query_1)
        self.drs_db._do_execute.assert_any_call(expected_query_2)
        self.assertEqual(result, [[{'OBJ_ID': 1, 'OIS_URN': 'urn:1'},
                                   {'OBJ_ID': 2, 'OIS_URN': 'urn:2'},
                                   {'OBJ_ID': 3, 'OIS_URN': 'urn:3'}]])

    def test_get_file_details_by_obj_id(self):
        obj_id = 1
        self.mock_cursor.fetchone.return_value = (5, 1024)

        result = self.drs_db.get_file_details_by_obj_id(obj_id)

        expected_query = """
        SELECT COUNT(*), SUM(df.FILE_SIZE)
        FROM REPOSITORY.DRS_FILE df
        WHERE df.DRS_OBJECT_ID = '1'
        """
        self.drs_db._do_execute.assert_called_once_with(expected_query)
        self.assertEqual(result, {"FILE_COUNT": 5,
                                  "FILE_BYTES": 1024,
                                  "OBJ_ID": obj_id})


if __name__ == '__main__':
    unittest.main()
