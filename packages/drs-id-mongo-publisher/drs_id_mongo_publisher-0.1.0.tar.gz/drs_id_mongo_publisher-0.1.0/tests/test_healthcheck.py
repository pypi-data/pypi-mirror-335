import pytest
from unittest.mock import MagicMock, patch
from drs_id_mongo_publisher.healthcheck import Healthcheck


@pytest.fixture
def mock_env_details():
    env_name = "drs_id_mongo_publisher.healthcheck.EnvDetails"
    with patch(env_name) as MockEnvDetails:
        mock_env = MockEnvDetails.return_value
        mock_env.get_mongo_collection.return_value = "test_collection"
        yield mock_env


@pytest.fixture
def mock_logger():
    logger_name = "drs_id_mongo_publisher.healthcheck.configure_logger"
    with patch(logger_name) as MockLogger:
        yield MockLogger


@pytest.fixture
def healthcheck(mock_env_details, mock_logger):
    mock_db = MagicMock()
    mock_mongo = MagicMock()
    return Healthcheck(mock_db, mock_mongo, "test_env")


def test_check_healthy(healthcheck):
    # Mock database and MongoDB behaviors
    healthcheck.db.get_format_count.return_value = 10
    healthcheck.mongo.list_collections.return_value = ["test_collection"]

    # Perform the health check
    result_db = healthcheck.check_db()
    result_mongo = healthcheck.check_mongo()

    # Assert the result is True
    assert result_db is True
    assert result_mongo is True
    healthcheck.db.get_format_count.assert_called_once()
    healthcheck.mongo.list_collections.assert_called_once()


def test_check_unhealthy_db(healthcheck):
    # Mock unhealthy database and healthy MongoDB
    healthcheck.db.get_format_count.return_value = 0
    healthcheck.mongo.list_collections.return_value = ["test_collection"]

    # Perform the health check
    result_db = healthcheck.check_db()
    result_mongo = healthcheck.check_mongo()

    # Assert the result is False
    assert result_db is False
    assert result_mongo is True
    healthcheck.db.get_format_count.assert_called_once()
    healthcheck.mongo.list_collections.assert_called_once()


def test_check_unhealthy_mongo(healthcheck):
    # Mock healthy database and unhealthy MongoDB
    healthcheck.db.get_format_count.return_value = 10
    healthcheck.mongo.list_collections.return_value = []

    # Perform the health check
    result_db = healthcheck.check_db()
    result_mongo = healthcheck.check_mongo()

    # Assert the result is False
    assert result_db is True
    assert result_mongo is False
    healthcheck.db.get_format_count.assert_called_once()
    healthcheck.mongo.list_collections.assert_called_once()


def test_check_exception_db(healthcheck):
    # Mock database and MongoDB to raise an exception
    healthcheck.db.get_format_count.side_effect = Exception("Database error")

    # Perform the health check
    result = healthcheck.check_db()

    # Assert the result is False
    assert result is False
    healthcheck.db.get_format_count.assert_called_once()


def test_check_exception_mongo(healthcheck):
    # Mock database and MongoDB to raise an exception
    healthcheck.mongo.list_collections.side_effect = Exception("MongoDB error")

    # Perform the health check
    result = healthcheck.check_mongo()

    # Assert the result is False
    assert result is False
    healthcheck.mongo.list_collections.assert_called_once()
