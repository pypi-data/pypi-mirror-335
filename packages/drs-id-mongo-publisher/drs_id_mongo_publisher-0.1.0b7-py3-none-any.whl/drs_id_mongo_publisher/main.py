from drs_id_mongo_publisher.healthcheck import Healthcheck
from drs_id_mongo_publisher.utils.utils_mongo import MongoUtil
from drs_id_mongo_publisher.utils.utils_db import DrsDB
from drs_id_mongo_publisher.runner import Runner
import argparse


def _do_healthcheck(environment):
    db = DrsDB(environment)
    mongo = MongoUtil(environment)
    healthcheck = Healthcheck(db, mongo, environment)
    result_db = healthcheck.check_db()
    result_mongo = healthcheck.check_mongo()
    print(f"Healthcheck results: db:{result_db}, mongo:{result_mongo}")


def _get_ids_list(ids_file):
    if ids_file is None:
        return None
    with open(ids_file, 'r') as file:
        ids_list = [line.strip() for line in file if line.strip()]
    return ids_list


def main():
    """
    Main entry point for the script.
    """
    ap = argparse.ArgumentParser(description='Collect DRS Object details '
                                 'from the DRS DB and store '
                                 'them in a Mongo DB.')
    ap.add_argument('-e', '--environment',
                    required=True,
                    help='Must be one of: dev, qa, prod')
    ap.add_argument('-f', '--ids_file',
                    required=False,
                    help='A list of DRS object ids to process. '
                         'If not provided, '
                         'all objects will be processed.')
    ap.add_argument('--dryrun',
                    action='store_true',
                    required=False,
                    help='Run the script in dry run mode without '
                         'making any changes.')
    ap.add_argument('--limit',
                    required=False,
                    type=int,
                    default=None,
                    help='Limit the number of objects to process. '
                         'If not provided, all objects will be processed.')
    ap.add_argument('--after',
                    required=False,
                    type=int,
                    default=None,
                    help='Process objects after a specific Object ID. '
                         'If not provided, all objects will be processed.')
    ap.add_argument('--batch_size',
                    required=False,
                    type=int,
                    default=1000,
                    help='Number of records to process in a batch. '
                         'If not provided, the default is 1000.')
    ap.add_argument('--healthcheck',
                    action='store_true',
                    required=False,
                    help='Perform healthcheck on DRS DB and Mongo. If this '
                         'flag is set, the script will only perform '
                         'healthcheck.')

    args = vars(ap.parse_args())

    environment = args['environment']
    if environment not in ['dev', 'qa', 'prod']:
        raise ValueError("Environment must be one of: dev, qa, prod")

    healthcheck = args['healthcheck']
    if healthcheck:
        _do_healthcheck(environment)
        # stop here if only healthcheck is requested
        return

    dryrun = args['dryrun']
    if dryrun:
        print("Running in dry run mode. No changes will be made.")

    limit = args['limit']
    after = args['after']
    batch_size = args['batch_size']

    db = DrsDB(environment)
    mongo = MongoUtil(environment, dryrun)
    runner = Runner(db, mongo, dryrun)

    ids_list = None
    if args['ids_file']:
        urn_file = args['ids_file']
        ids_list = _get_ids_list(urn_file)
    runner.run(limit, after, ids_list, batch_size)


if __name__ == "__main__":
    main()
