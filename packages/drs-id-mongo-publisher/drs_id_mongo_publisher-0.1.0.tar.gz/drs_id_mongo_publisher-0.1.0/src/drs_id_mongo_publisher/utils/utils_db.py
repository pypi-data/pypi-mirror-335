import oracledb
from dotenv import load_dotenv
from drs_id_mongo_publisher import configure_logger
from .utils_env import EnvDetails


class DrsDB:

    def __init__(self, env, dryrun=False):
        # Load environment variables from .env file
        load_dotenv()
        self.env = env
        self.db = self._get_db_connection(env)
        self.logger = configure_logger(__name__)

    def get_obj_details_all(self):
        obj_id_itr = self._get_obj_ids_all()  # Get iterator of all object IDs

        # Fetch details using the iterator
        object_details = self.get_obj_details_by_obj_ids(obj_id_itr)
        return object_details

    def _get_obj_ids_all(self):
        query = """
        SELECT do.id as "DRS_OBJECT_ID"
        FROM REPOSITORY.DRS_OBJECT do
        ORDER BY do.id
        """
        cursor = self._do_execute(query)

        batch_size = 10000  # Adjust based on memory and performance
        while True:
            result = cursor.fetchmany(batch_size)  # Fetch a batch of rows
            if not result:
                break  # Stop when no more data is available

            for row in result:
                yield row[0]  # Yielding each ID individually

    def get_obj_details_by_obj_ids(self, obj_id_itr, chunk_size=1000):
        query_template = """
        SELECT do.id as "DRS_OBJECT_ID", do.OIS_URN
        FROM REPOSITORY.DRS_OBJECT do WHERE do.id IN (:ids)
        """

        # Function to split the IDs into manageable chunks
        def chunked_iterator(iterator, size):
            batch = []
            for item in iterator:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch

        results = []

        # Process each chunk of IDs
        for chunk in chunked_iterator(obj_id_itr, chunk_size):
            id_string = ', '.join(f"'{id}'" for id in chunk)
            query = query_template.replace(":ids", id_string)
            cursor = self._do_execute(query)
            batch_result = cursor.fetchall()
            results.extend([
                {"OBJ_ID": row[0], "OIS_URN": row[1]} for row in batch_result])

        # Wrap the result in a list of lists to match the expected format
        return [results]

    def get_file_details_by_obj_id(self, obj_id):
        query_template = """
        SELECT COUNT(*), SUM(df.FILE_SIZE)
        FROM REPOSITORY.DRS_FILE df
        WHERE df.DRS_OBJECT_ID = :id
        """

        query = query_template.replace(":id", f"'{obj_id}'")
        self.logger.debug(f"Get file details from DB, obj_id: {obj_id}")
        cursor = self._do_execute(query)
        row = cursor.fetchone()

        return {"FILE_COUNT": row[0],
                "FILE_BYTES": row[1],
                "OBJ_ID": obj_id}

    def get_format_count(self):
        query = """
        SELECT COUNT(*)
        FROM REPOSITORY.FORMAT
        """
        cursor = self._do_execute(query)
        row = cursor.fetchone()
        return row[0]

    def _do_execute(self, query, retry=True):
        error = None
        if self.db is None:
            self.db = self._get_db_connection(self.env)

        cursor = self.db.cursor()

        try:
            cursor.execute(query)
        except oracledb.DatabaseError as e:
            if cursor:
                cursor.close()
            if self.db:
                self.db.close()
                self.db = None

            if retry:
                self.logger.debug(f"Retrying: {query}")
                return self._do_execute(query, retry=False)

            else:
                error, = e.args
                self.logger.error(f"Error: {error.code} - {error.message}")
                raise Exception(f"Error: {error.code} - {error.message}")

        return cursor

    def _get_db_connection(self, env):
        env_details = EnvDetails(env)

        dsn_tns = oracledb.makedsn(env_details.get_db_host(),
                                   env_details.get_db_port(),
                                   env_details.get_db_name())

        # Oracle database connection details
        db = oracledb.connect(
            user=env_details.get_db_user(),
            password=env_details.get_db_pass(),
            dsn=dsn_tns
        )

        return db
