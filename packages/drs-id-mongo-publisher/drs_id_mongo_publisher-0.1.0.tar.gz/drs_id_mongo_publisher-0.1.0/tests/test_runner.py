import unittest
from unittest.mock import MagicMock, patch

import pytest
from drs_id_mongo_publisher.runner import Runner
from drs_id_mongo_publisher.model.obj_description import ObjectDescription


class TestRunner(unittest.TestCase):

    def setUp(self):
        self.db_mock = MagicMock()
        self.mongo_mock = MagicMock()
        self.runner = Runner(self.db_mock, self.mongo_mock)

    @patch('drs_id_mongo_publisher.runner.configure_logger')
    def test_run(self, mock_configure_logger):
        self.runner._do_run = MagicMock()
        self.runner.run()
        self.runner._do_run.assert_called_once()
        self.mongo_mock.close_connection.assert_called_once()

    def test_do_run(self):
        obj_desc1 = MagicMock()
        obj_desc1.obj_id = 123
        obj_desc2 = MagicMock()
        obj_desc2.obj_id = 124
        self.runner._get_objs_from_drs = MagicMock(return_value=[
            [obj_desc1, obj_desc2]])
        self.runner._to_record = MagicMock(side_effect=lambda x: x)
        self.runner._do_run()
        self.mongo_mock.insert_many.assert_called()

    def test_do_run_with_limit(self):
        obj_desc1 = MagicMock()
        obj_desc1.obj_id = 123
        obj_desc2 = MagicMock()
        obj_desc2.obj_id = 124
        self.runner._get_objs_from_drs = MagicMock(return_value=[
            [obj_desc1, obj_desc2]])

        self.runner._to_record = MagicMock(side_effect=lambda x: x)
        self.runner._do_run(limit=1)
        self.mongo_mock.insert_many.assert_called_once()
        self.assertEqual(self.mongo_mock.insert_many.call_count, 1)

    def test_get_objs_from_drs(self):
        self.db_mock.get_obj_details_by_obj_ids.return_value = [
            [{"OBJ_ID": 1234, "OIS_URN": "urn-3:HUL.DRS.OBJECT:31852370"},
             {"OBJ_ID": 5678, "OIS_URN": "urn-3:HUL.DRS.OBJECT:31852371"}]]
        ids_list = [1234, 5678]
        result = list(self.runner._get_objs_from_drs(ids_list))

        self.assertEqual(len(result[0]), 2, result)

    def test_get_object_description(self):
        obj_details = {'OBJ_ID': '123'}
        with pytest.raises(ValueError):
            obj_description = ObjectDescription(obj_details)
            self.assertIsInstance(obj_description, ObjectDescription)

    def test_to_record(self):
        obj_description = MagicMock()
        obj_description.obj_id = 123
        obj_description.ois_urn = 'urn-3:HUL.DRS.OBJECT:31852370'
        record = self.runner._to_record(obj_description)
        self.assertEqual(record['_id'], 123)
        self.assertEqual(record['ocfl_object_key'], '0732/5813/31852370')
        self.assertEqual(record['validation_status'], 'pending')

    def test_urn_to_path(self):
        urn = 'urn-3:HUL.DRS.OBJECT:31852370'
        path = self.runner._urn_to_path(urn)
        self.assertEqual(path, '0732/5813/31852370')


if __name__ == '__main__':
    unittest.main()
