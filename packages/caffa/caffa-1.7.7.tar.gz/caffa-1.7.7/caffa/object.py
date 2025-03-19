###################################################################################################
#
#   Caffa
#   Copyright (C) Kontur AS
#
#   GNU Lesser General Public License Usage
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation; either version 2.1 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.
#
#   See the GNU Lesser General Public License at <<http:#www.gnu.org/licenses/lgpl-2.1.html>>
#   for more details.
#
import json
import logging


class Object(object):
    """
    A wrapper class for a JSON-backed object received from a Caffa Rest Interface.
    The object will dynamically be assigned Python attributes (fields) based on the JSON schemas provided by the server.

    If the underlying JSON object contains an attribute "test_string" it can be read like:
    print(object.test_string)
    ... or assigned like
    object.test_string = "a test string"

    The Caffa Objects will also dynamically get assigned methods based on the JSON content by the server.
    The names of these can be accessed with the methods() method.
    """

    _log = logging.getLogger("caffa-object")

    def __init__(self, json_object="", client=None, local=False):
        """
        Initialise the object with a dict or JSON string and optionally a client connection.
        Caffa Objects are not generally created by the user. Instead they are returned by the RestClient class.

        Args:
            json_object: A dict or JSON string
            client: A rest-client object
            local: True if the object has locally stored attributes. False read remotely
        """
        if isinstance(json_object, dict):
            self._fields = json_object
        else:
            self._fields = json.loads(json_object)

        self._client = client
        self._local = local

        if not self._local:
            assert self._client is not None

        self._method_list = []
        if hasattr(self.__class__, "_methods"):
            for method in self.__class__._methods:
                method_instance = method(self_object=self)
                setattr(self, method_instance.name(), method_instance)
                self._method_list.append(method_instance)

        # Avoid the custom __setattr__() method
        object.__setattr__(self, "__instantiated", True)

    @property
    def keyword(self):
        """
        The class keyword of the object

        Returns:
            A keyword string
        """
        return self._fields["keyword"]

    def get(self, field_keyword):
        """
        Get an attribute of the JSON object. This will be called when accessing the field as an attribute
        value = object.field_keyword

        Args:
            field_keyword: The name of the attribute

        Returns:
            The value of the attribute. Can be any JSON backed type or another Caffa Object

        Raises:
            RuntimeError: If the field does not exist or is not readable
        """
        from .object_creator import create_class

        value = None
        if not self._local and field_keyword != "keyword" and field_keyword != "uuid":
            value = json.loads(
                self._client.get_field_value(self._fields["uuid"], field_keyword)
            )
        elif self._fields and field_keyword in self._fields:
            value = self._fields[field_keyword]

        if isinstance(value, dict):
            keyword = value["keyword"]
            schema_location = ""
            if "$id" in value:
                schema_location = value["$id"]
            else:
                schema_location = self._client.schema_location_from_keyword(keyword)

            schema_properties = self._client.schema_properties(schema_location)
            cls = create_class(keyword, schema_properties)
            value = cls(value, self._client, self._local)
        return value

    def set(self, field_keyword, value):
        """
        Set an attribute of the JSON object

        Args:
            field_keyword: The name of the attribute
            value: The value of the attribute. Can be any JSON backed type or another Caffa Object

        Raises:
            RuntimeError: If the field does not exist or is not writable
        """

        if isinstance(value, Object):
            value = value.to_json()
        if not self._local:
            self._client.set_field_value(self.uuid, field_keyword, value)
        else:
            if hasattr(self._fields[field_keyword], "value"):
                self._fields[field_keyword]["value"] = value
            else:
                self._fields[field_keyword] = value

    def _execute(self, object_method, arguments):
        """
        PRIVATE: Execute an object method. Used internally by caffa

        Args:
          object_method: The method object
          arguments: The list of arguments

          Raises:
              RuntimeError: If the method does not exist or fails to execute on the server
        """
        return self._client.execute(self.uuid, object_method.name(), arguments)

    def methods(self):
        """
        Get a list of methods available to run on the object

        Returns:
            A list of methods (Caffa Method object)
        """
        return self._method_list

    def to_dict(self):
        """
        Create a Python dictionary representation of the object with key/value pairs

        Returns:
            Python dictionary
        """
        content = {}
        for key in self._fields:
            value = self.get(key)
            if isinstance(value, Object):
                value = value.to_dict()
            content[key] = value
        return content

    def to_json(self):
        """
        Get a Python JSON representation of the Caffa object

        Returns:
            A Python JSON object
        """
        return json.loads(self.to_string())

    def to_string(self):
        """
        Get a JSON string representation of the Caffa object

        Return:
            A JSON string
        """
        return json.dumps(self.to_dict())

    def __is_instantiated(self):
        return hasattr(self, "__instantiated") and getattr(self, "__instantiated")

    def __setattr__(self, key, value):
        # Do not allow new attributes to be set on objects that are instantiated
        if not hasattr(self, key) and self.__is_instantiated():
            raise TypeError("%r does not have the property %s", self, key)
        object.__setattr__(self, key, value)
