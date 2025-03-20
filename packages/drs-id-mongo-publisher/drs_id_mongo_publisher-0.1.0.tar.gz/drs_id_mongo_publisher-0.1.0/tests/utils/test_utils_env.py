import os
import pytest
from unittest import mock
from drs_id_mongo_publisher.utils.utils_env import EnvDetails


# Environment variables fixture
@pytest.fixture
def env_setup():
    with mock.patch.dict(os.environ, {
        'test_db_user': 'test_user',
        'test_db_pass': 'test_pass',
        'test_db_host': 'test_host',
        'test_db_port': 'test_port',
        'test_db_name': 'test_db',
        'test_mongo_url': 'test_mongo_url',
        'test_mongo_db': 'test_mongo_db',
        'test_mongo_collection': 'test_mongo_collection'
    }):
        yield


@pytest.fixture
def env_details(env_setup):
    return EnvDetails('test')


@pytest.mark.parametrize("attr, expected", [
    ("get_db_user", 'test_user'),
    ("get_db_pass", 'test_pass'),
    ("get_db_host", 'test_host'),
    ("get_db_port", 'test_port'),
    ("get_db_name", 'test_db'),
    ("get_mongo_url", 'test_mongo_url'),
    ("get_mongo_db", 'test_mongo_db'),
    ("get_mongo_collection", 'test_mongo_collection')
])
def test_env_details(env_details, attr, expected):
    assert getattr(env_details, attr)() == expected


def test_missing_env_var():
    with mock.patch.dict(os.environ, {}, clear=True):
        env = EnvDetails('test')
        assert env.get_db_user() is None
        assert env.get_db_pass() is None
        assert env.get_db_host() is None
        assert env.get_db_port() is None
        assert env.get_db_name() is None
        assert env.get_mongo_url() is None
        assert env.get_mongo_db() is None
        assert env.get_mongo_collection() is None
