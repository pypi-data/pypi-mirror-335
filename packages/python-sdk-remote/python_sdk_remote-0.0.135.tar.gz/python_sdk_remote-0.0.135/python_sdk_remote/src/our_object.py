import json
from abc import ABC  # , abstractmethod
from datetime import datetime

from .mini_logger import MiniLogger as logger


# TODO Where are we using it? Shall we extend the usage of OurObject as the father of all our entities?
class OurObject(ABC):
    def __init__(self, id_column_name, **kwargs):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME, object={'kwargs': kwargs})
        setattr(self, 'id_column_name', id_column_name)
        for field, value in kwargs.items():
            # if field in event_fields:
            setattr(self, field, value)

        # self.kwargs = kwargs
        logger.end(INIT_METHOD_NAME, object={'kwargs': kwargs})

    def get_id_column_name(self):
        """Returns the id of the object"""
        return self.get('id_column_name')

    # Commented so we can use it in database foreach()
    # @abstractmethod
    def get_name(self):
        """Returns the name of the object"""
        # raise NotImplementedError(
        # "Subclasses must implement the 'get_name' method.")

    def get(self, attr_name: str):
        """Returns the value of the attribute with the given name"""
        GET_METHOD_NAME = 'get'
        logger.start(GET_METHOD_NAME, object={'attr_name': attr_name})
        # arguments = getattr(self, 'kwargs', None)
        # value = arguments.get(attr_name, None)
        value = self.__dict__.get(attr_name, None)
        logger.end(GET_METHOD_NAME, object={'attr_name': attr_name})
        return value

    def get_all_arguments(self):
        """Returns all the arguments passed to the constructor as a dictionary"""
        # return getattr(self, 'kwargs', None)
        return self.__dict__

    def to_json(self) -> str:
        """Returns a json string representation of this object"""
        return json.dumps(self.__dict__, default=self._serialize)

    @staticmethod
    def _serialize(obj):
        """Custom serialization function for unsupported types. Used by json.dumps"""
        if isinstance(obj, datetime):
            return obj.isoformat()  # Converts datetime to ISO 8601 string
        raise TypeError(f"Type {type(obj)} not serializable")

    def from_json(self, json_string: str) -> 'OurObject':
        """Returns an instance of the class from a json string"""
        FROM_JSON_METHOD_NAME = 'from_json'
        logger.start(FROM_JSON_METHOD_NAME,
                     object={'json_string': json_string})
        self.__dict__ = json.loads(json_string)
        logger.end(FROM_JSON_METHOD_NAME,
                   object={'json_dict': self.__dict__})
        return self

    def __eq__(self, other) -> bool:
        """Checks if two objects are equal"""
        if not isinstance(other, OurObject):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other) -> bool:
        """Checks if two objects are not equal"""
        return not self.__eq__(other)

    def get_dict(self):
        return self.__dict__
