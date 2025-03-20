from dataclasses import dataclass, field, fields, is_dataclass
from pprint import pprint
from sys import version_info
# to compare package versions
from packaging.version import Version
from numpy import ndarray, integer, floating, complexfloating, issubdtype
from typing import Any
from typing import Generator
from idspy_dictionaries._version import _IDSPY_VERSION, _IDSPY_IMAS_DD_GIT_COMMIT, \
    _IDSPY_IMAS_DD_VERSION, _IDSPY_INTERNAL_VERSION

default_version = (3, 10)
min_version = (3, 9)
cur_version = version_info

__IDSPY_USE_SLOTS = True


def idspy_dataclass(*args, **kwargs):
    # Check Python version
    has_slots = version_info >= default_version
    if not has_slots:
        # Add or modify the 'slots' argument based on Python version
        if 'slots' in kwargs:
            kwargs.pop('slots')

    # Use the original dataclass decorator
    return dataclass(*args, **kwargs)


class StructArray(list):
    type_items: Any = None

    def __init__(self, iterable: list = None, type_input: Any = None):
        if isinstance(type_input, (list, tuple)):
            raise TypeError("type_input cannot be a list of type")
        if type_input:
            if not is_dataclass(type_input):
                raise TypeError(f"type_input must be equivalent to a dataclass and not a {type_input}")
        self.type_items = type_input

        if iterable is not None:
            super().__init__(item for item in iterable)

    def append(self, item: Any) -> None:
        if not is_dataclass(item):
            raise TypeError(f"Item for a StructArray must be a dataclass or derived from a dataclass and not a {type(item)}")

        if self.type_items is not None:
            if not isinstance(item, self.type_items):
                raise TypeError(f"Item must be of type {self.type_items.__name__} and not {type(item)}")
        else:
            self.type_items = type(item)

        super().append(item)

    def getStructArrayElement(self):
        return self.type_items()


@idspy_dataclass(slots=__IDSPY_USE_SLOTS, frozen=True)
class IdsVersion:
    """Class representing version information for IDS.

    This class stores version information for different components of the IDS system
    and provides comparison operations between versions.

    Attributes:
        idspy_version (str): Version of the IDSPY package
        imas_dd_git_commit (str): Git commit hash of the IMAS data dictionary
        imas_dd_version (str): Version of the IMAS data dictionary
        idspy_internal_version (str): Internal version number of IDSPY
    """
    idspy_version: str = field(default=_IDSPY_VERSION)
    imas_dd_git_commit: str = field(default=_IDSPY_IMAS_DD_GIT_COMMIT)
    imas_dd_version: str = field(default=_IDSPY_IMAS_DD_VERSION)
    idspy_internal_version: str = field(default=_IDSPY_INTERNAL_VERSION)

    def __eq__(self, other):
        """Equal comparison operator.

        Args:
            other (Union[str, IdsVersion]): Version to compare with, either as string or IdsVersion object

        Returns:
            bool: True if versions are equal, False otherwise
            NotImplemented: If other is neither string nor IdsVersion
        """
        if isinstance(other, str):
            return Version(self.idspy_version) == Version(other)
        elif isinstance(other, IdsVersion):
            return Version(self.idspy_version) == Version(other.idspy_version)
        return NotImplemented

    def __lt__(self, other):
        """Less than comparison operator.

        Args:
            other (Union[str, IdsVersion]): Version to compare with, either as string or IdsVersion object

        Returns:
            bool: True if self version is less than other version, False otherwise
            NotImplemented: If other is neither string nor IdsVersion
        """
        if isinstance(other, str):
            return Version(self.idspy_version) < Version(other)
        elif isinstance(other, IdsVersion):
            return Version(self.idspy_version) < Version(other.idspy_version)
        return NotImplemented

    def __gt__(self, other):
        """Greater than comparison operator.

        Args:
            other (Union[str, IdsVersion]): Version to compare with, either as string or IdsVersion object

        Returns:
            bool: True if self version is greater than other version, False otherwise
            NotImplemented: If other is neither string nor IdsVersion
        """
        if isinstance(other, str):
            return Version(self.idspy_version) > Version(other)
        elif isinstance(other, IdsVersion):
            return Version(self.idspy_version) > Version(other.idspy_version)
        return NotImplemented

    def __le__(self, other):
        """Less than comparison operator.

        Args:
            other (Union[str, IdsVersion]): Version to compare with, either as string or IdsVersion object

        Returns:
            bool: True if self version is less than other version, False otherwise
            NotImplemented: If other is neither string nor IdsVersion
        """
        if isinstance(other, str):
            return Version(self.idspy_version) <= Version(other)
        elif isinstance(other, IdsVersion):
            return Version(self.idspy_version) <= Version(other.idspy_version)
        return NotImplemented

    def __ge__(self, other):
        """Greater than comparison operator.

        Args:
            other (Union[str, IdsVersion]): Version to compare with, either as string or IdsVersion object

        Returns:
            bool: True if self version is greater than other version, False otherwise
            NotImplemented: If other is neither string nor IdsVersion
        """
        if isinstance(other, str):
            return Version(self.idspy_version) >= Version(other)
        elif isinstance(other, IdsVersion):
            return Version(self.idspy_version) >= Version(other.idspy_version)
        return NotImplemented

@idspy_dataclass(slots=__IDSPY_USE_SLOTS)
class IdsBaseClass:
    """
        Base class used for all the IDS
    """
    # any class member of this class will be ignored for DB insertion etc
    max_repr_length: int = 64
    version: IdsVersion = IdsVersion()

    @property
    def print_ids(self) -> object:
        """
            print IDS field values
        """
        pprint(f"current ids : {self}", indent=2)
        return None

    @classmethod
    def _get_root_members(cls)->tuple:
        return tuple([x.name for x in fields(IdsBaseClass)])

    def get_members_name(self)-> Generator[str, None, None]:
        """
            get a tuple of current IDS members
        """
        return (x.name for x in fields(self) if x.name not in IdsBaseClass._get_root_members())

    def __repr__(self):
        class_fields = fields(self)
        field_list = []
        for f in class_fields:
            value = getattr(self, f.name)
            if isinstance(value, (ndarray,)):
                if len(repr(value)) > self.max_repr_length:
                    value = repr(value)[:self.max_repr_length] + "..."
            field_list.append(f"{f.name}={value}\n")
        return f"{self.__class__.__qualname__}(" + ", ".join(field_list) + ")"