from drs_id_mongo_publisher import configure_logger


class ObjectDescription:

    def __init__(self, obj_details):
        # Error handling for missing or invalid obj_details
        if obj_details is None:
            raise ValueError("obj_details cannot be None")
        if 'OIS_URN' not in obj_details:
            raise ValueError("obj_details must contain 'OIS_URN'")
        if 'OBJ_ID' not in obj_details:
            raise ValueError("obj_details must contain 'OBJ_ID'")

        self.logger = configure_logger(__name__)
        self.ois_urn = obj_details['OIS_URN']
        self.obj_id = obj_details['OBJ_ID']

    @property
    def obj_id(self):
        return self._obj_id

    @obj_id.setter
    def obj_id(self, value):
        self._obj_id = value

    def __str__(self) -> str:
        return "{},{}".format(
            self.obj_id,
            self.ois_urn)

    def __repr__(self) -> str:
        return f"ObjectDescription: {self.obj_id}, {self.ois_urn}"
