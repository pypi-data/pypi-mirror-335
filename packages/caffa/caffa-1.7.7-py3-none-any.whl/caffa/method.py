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
import logging


class Method:
    """
    A class representing a remote procedure call that can be run on a Caffa Object
    """

    _log = logging.getLogger("caffa-method")
    _labelled_arguments = {}
    _positional_arguments = {}

    def __init__(self, self_object):
        self._self_object = self_object

    def __call__(self, *args, **kwargs):
        from .object import Object

        arguments = {}
        if len(kwargs.items()) > 0:
            arguments["labelledArguments"] = self.__class__._labelled_arguments[
                self.__class__.__name__
            ]
            for key, value in kwargs.items():
                if isinstance(value, Object):
                    value = value.to_dict()
                arguments["labelledArguments"][key] = value
        elif len(args) > 0:
            arguments["positionalArguments"] = self.__class__._positional_arguments[
                self.__class__.__name__
            ]
            for i, value in enumerate(args):
                if isinstance(value, Object):
                    value = value.to_dict()
                arguments["positionalArguments"][i] = value

        return self._self_object._execute(self, arguments)

    def name(self):
        """
        Get the name of the method

        Returns:
            String containing the method name
        """
        return self.__class__.__name__
