import os
from dotenv import load_dotenv


class EnvDetails:
    def __init__(self, e):
        self.env = e
        # Load environment configuration
        load_dotenv()

    def get_db_user(self):
        return os.getenv('{}_db_user'.format(self.env))

    def get_db_pass(self):
        return os.getenv('{}_db_pass'.format(self.env))

    def get_db_host(self):
        return os.getenv('{}_db_host'.format(self.env))

    def get_db_port(self):
        return os.getenv('{}_db_port'.format(self.env))

    def get_db_name(self):
        return os.getenv('{}_db_name'.format(self.env))

    def get_mongo_url(self):
        return os.getenv('{}_mongo_url'.format(self.env))

    def get_mongo_db(self):
        return os.getenv('{}_mongo_db'.format(self.env))

    def get_mongo_collection(self):
        return os.getenv('{}_mongo_collection'.format(self.env))
