from drs_id_mongo_publisher import configure_logger
from drs_id_mongo_publisher.utils.utils_env import EnvDetails


class Healthcheck:

    def __init__(self, db, mongo, environment):
        self.env = EnvDetails(environment)
        self.db = db
        self.mongo = mongo
        self.logger = configure_logger(__name__)

    def check_db(self) -> bool:
        healthy_db = False
        try:
            # check if the database is up and running
            count = self.db.get_format_count()
            healthy_db = count > 0

            return healthy_db
        except Exception:
            self.logger.exception(f"Healthcheck failed! db:{healthy_db}")
            return False

    def check_mongo(self) -> bool:
        healthy_mongo = False
        try:
            # check if MongoDB is able to perform a find operation
            name = self.env.get_mongo_collection()
            collections = self.mongo.list_collections()
            healthy_mongo = len(collections) > 0 and name in collections

            return healthy_mongo
        except Exception:
            self.logger.exception(f"Healthcheck failed! mongo:{healthy_mongo}")
            return False

    def __call__(self):
        return self.check()
