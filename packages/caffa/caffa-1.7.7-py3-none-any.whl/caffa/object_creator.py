from .object import Object
from .method import Method


def prep_attributes(cls):
    setattr(cls, "_fields", None)
    setattr(cls, "_client", None)
    setattr(cls, "_local", None)
    setattr(cls, "_method_list", None)


def make_read_lambda(property_name):
    return lambda self: self.get(property_name)


# Dummy read lambda used to avoid a proper caffa read call when asking
# for a write-only attribute
def make_dummy_read_lambda(property_name):
    return lambda self: None


def make_write_lambda(property_name):
    return lambda self, value: self.set(property_name, value)


def raise_write_exception(property_name):
    raise AttributeError("Property " + property_name + " is read only!")


def make_write_error_lambda(property_name):
    return lambda value: raise_write_exception(property_name)


def create_class(name, schema_properties):
    def __init__(self, json_object="", client=None, local=False):
        Object.__init__(self, json_object, client, local)

    newclass = type(name, (Object,), {"__init__": __init__})
    newclass._methods = []

    for property_name, prop in schema_properties.items():
        if property_name != "keyword" and property_name != "methods":
            read_only = "readOnly" in prop and prop["readOnly"]
            write_only = "writeOnly" in prop and prop["writeOnly"]

            read_lambda = make_dummy_read_lambda(property_name)
            write_lambda = make_write_error_lambda(property_name)

            if not write_only:
                read_lambda = make_read_lambda(property_name)
            if not read_only:
                write_lambda = make_write_lambda(property_name)

            setattr(
                newclass,
                property_name,
                property(
                    fget=read_lambda,
                    fset=write_lambda,
                ),
            )
        elif property_name == "methods":
            for method_name, method_schema in prop["properties"].items():
                method_schema = method_schema["properties"]
                newclass._methods.append(
                    create_method_class(method_name, method_schema)
                )
    prep_attributes(newclass)
    return newclass


def create_method_class(name, schema):
    def __init__(self, self_object):
        return Method.__init__(self, self_object)

    newclass = type(name, (Method,), {"__init__": __init__})
    newclass._labelled_arguments[name] = {}
    newclass._positional_arguments[name] = []
    if "labelledArguments" in schema:
        for argument_name in schema["labelledArguments"]["properties"]:
            newclass._labelled_arguments[name][argument_name] = None
    if "positionalArguments" in schema:
        for i, entry in enumerate(schema["positionalArguments"]["items"]):
            newclass._positional_arguments[name].append(None)

    return newclass
