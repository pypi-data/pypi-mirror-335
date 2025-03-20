from dotenv import load_dotenv
import pymongo

from drs_id_mongo_publisher import configure_logger
from drs_id_mongo_publisher.utils.utils_env import EnvDetails


class MongoUtil():

    def __init__(self, env, dryrun=False):
        # Load environment variables from .env file
        load_dotenv()

        self.dryrun = dryrun
        self.client = self._get_mongo_client(env)
        self.db = self._get_mongo_db(env, self.client)
        self.collection = self._get_mongo_collection(env, self.db)
        self.logger = configure_logger(__name__)

    def insert_record(self, record):
        self.logger.debug(f"insert_record: {record}")
        self.collection.insert_one(record)

    def insert_many(self, records):
        self.logger.debug(f"insert_records: {len(records)}")
        try:
            self.logger.info(f"Attempting to insert {len(records)} "
                             f"records into MongoDB: last: {records[-1]}")
            if not self.dryrun:
                self.collection.insert_many(records)

        except pymongo.errors.BulkWriteError as bwe:
            self.logger.error(f"BulkWriteError: {bwe.details}")
            raise bwe

    def list_collections(self):
        return self.db.list_collection_names()

    def close_connection(self):
        if self.client is not None:
            self.client.close()

    def _get_mongo_client(self, env):
        env_details = EnvDetails(env)
        client = pymongo.MongoClient(env_details.get_mongo_url())
        return client

    def _get_mongo_db(self, env, client):
        env_details = EnvDetails(env)
        if client is None:
            raise ValueError("Mongo client is None. Cannot get Mongo DB.")

        return client[env_details.get_mongo_db()]

    def _get_mongo_collection(self, env, db):
        env_details = EnvDetails(env)
        if db is None:
            raise ValueError("Mongo DB is None. Cannot get Mongo Collection.")

        return db[env_details.get_mongo_collection()]
