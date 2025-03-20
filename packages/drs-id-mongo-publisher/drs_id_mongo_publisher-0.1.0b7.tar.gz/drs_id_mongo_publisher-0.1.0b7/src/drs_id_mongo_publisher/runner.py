from bson import Int64
from drs_id_mongo_publisher.model.obj_description import ObjectDescription
from drs_id_mongo_publisher import configure_logger


class Runner:

    def __init__(self, db, mongo, dryrun=True):
        self.db = db
        self.mongo = mongo
        self.dryrun = dryrun
        self.logger = configure_logger(__name__)

    def run(self, limit=None, after=None, ids_list=None, batch_size=1000):
        try:
            list_len = "len:id_list(0)" if ids_list is None \
                else f"len:id_list({len(ids_list)})"
            self.logger.info(f"Runner config: limit:{limit}, after:{after}, "
                             f"len:id_list({list_len}), "
                             f"dryrun:{self.dryrun}")
            self.logger.info("Starting the process...")
            self._do_run(limit, after, ids_list, batch_size)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
        finally:
            self.mongo.close_connection()

    def _do_run(self, limit=None, after=None, ids_list=None, batch_size=1000):
        # Retrieve object descriptions from the DRS
        batch = []  # This will store the batch of records

        # Number of records processed
        count = 0

        # If after is None, we have effectively reached the 'after' record
        after_reached = False
        if after is None:
            after = 0
            after_reached = True

        do_break = False

        for obj_descriptions in self._get_objs_from_drs(ids_list, batch_size):

            if do_break:
                break

            self.logger.debug(f"descriptions: {len(obj_descriptions)}")

            # Prepare object details to be written to Mongo
            for obj_description in obj_descriptions:

                # Have we reached the limit of records to process?
                if after_reached and limit is not None and count >= limit:
                    self.logger.info(f"Reached limit of {limit} records. "
                                     "Stopping processing before: {}".format(
                                         obj_description.obj_id))
                    do_break = True
                    break

                # Have we exceeded the 'after' record yet?
                after_reached = obj_description.obj_id > int(after)
                if after_reached:
                    mongo_record = self._to_record(obj_description)
                    batch.append(mongo_record)  # Append record to the batch

                    # Check if the batch size has reached 1000 records
                    if len(batch) >= batch_size:
                        self.mongo.insert_many(batch)
                        batch = []  # Clear the batch after insertion

                    count += 1

        # Insert any remaining records in the batch after loop finishes
        if batch:
            self.mongo.insert_many(batch)

    def _get_objs_from_drs(self, ids_list=None, batch_size=1000):
        # Get object detail sets from the DRS
        self.logger.info("Retrieving object details from DRS...")

        index = 0
        obj_details_itr = []
        if ids_list is None:
            self.logger.info("Processing all objects")
            obj_details_itr = self.db.get_obj_details_all()
        else:
            self.logger.info(f"Processing {len(ids_list)} objects")
            obj_details_itr = self.db.get_obj_details_by_obj_ids(ids_list)

        for obj_details in obj_details_itr:
            rows = []
            index += 1
            if (index) % 100 == 0:
                self.logger.info(
                    f"Processing set {index + 1}, {len(obj_details)}")

            # Get object details from each set
            for obj in obj_details:
                obj_description = ObjectDescription(obj)
                self.logger.info(f"obj_description: {obj_description.obj_id}")
                rows.append(obj_description)

                if len(rows) >= batch_size:
                    yield rows
                    rows = []  # Clear the batch after insertion

            if rows:
                yield rows

    def _to_record(self, obj_description):
        self.logger.debug(f"Creating record for MongoDB: {obj_description}")
        return {
            "_id": Int64(obj_description.obj_id),
            "ocfl_object_key": self._urn_to_path(obj_description.ois_urn),
            "validation_status": "pending",
        }

    def _urn_to_path(self, ois_urn):
        """This method converts an OIS URN into the OCFL path for an Object
        Example input: urn-3:HUL.DRS.OBJECT:31852370"""

        nss = ois_urn.upper().split("OBJECT:")[1]
        reverse = nss[::-1]
        first = reverse[0:4]
        second = reverse[4:8]
        return "%s/%s/%s" % (first, second, nss)
