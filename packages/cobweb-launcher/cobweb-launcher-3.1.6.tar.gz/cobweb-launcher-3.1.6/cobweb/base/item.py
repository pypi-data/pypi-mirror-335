from .seed import Seed
from collections import namedtuple


class Item(type):

    def __new__(cls, name, bases, dct):
        new_class_instance = type.__new__(cls, name, bases, dct)
        if name != "BaseItem":
            table = getattr(new_class_instance, "__TABLE__")
            fields = getattr(new_class_instance, "__FIELDS__")
            new_class_instance.Data = namedtuple(table, fields)
        return new_class_instance


class BaseItem(metaclass=Item):

    __TABLE__ = ""
    __FIELDS__ = ""

    def __init__(self, seed: Seed, **kwargs):
        self.seed = seed

        data = {}
        for key, value in kwargs.items():
            if key not in self.__FIELDS__:
                self.__setattr__(key, value)
            else:
                data[key] = value

        self.data = self.Data(**data)

    @property
    def to_dict(self):
        return self.data._asdict()

    @property
    def table(self):
        return self.Data.__name__


class ConsoleItem(BaseItem):

    __TABLE__ = "console"
    __FIELDS__ = "data"

