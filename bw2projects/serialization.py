import os
import pickle
import random
from collections.abc import MutableMapping
from time import time

from .errors import PickleError
from .fatomic import open as atomic_open
from .filesystem import maybe_path


class SerializedDict(MutableMapping):
    """Base class for dictionary that can be `serialized <http://en.wikipedia.org/wiki/Serialization>`_ to or unserialized from disk. Uses JSON as its storage format. Has most of the methods of a dictionary.

    Upon instantiation, the serialized dictionary is read from disk."""

    def __init__(self, dirpath):
        if not getattr(self, "filename"):
            raise NotImplementedError(
                "SerializedDict must be subclassed, and the filename must be set."
            )
        self.dirpath = maybe_path(dirpath)
        self.filepath = self.dirpath / self.filename
        self.load()

    def load(self):
        """Load the serialized data. Creates the file if not yet present."""
        try:
            self.data = self.deserialize()
        except IOError:
            # Create if not present
            self.data = {}
            self.flush()

    def flush(self):
        """Serialize the current data to disk."""
        self.serialize()

    @property
    def list(self):
        """List the keys of the dictionary. This is a property, and does not need to be called."""
        return sorted(self.data.keys())

    def __getitem__(self, key):
        if isinstance(key, list):
            key = tuple(key)
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.flush()

    def __contains__(self, key):
        return key in self.data

    def __str__(self):
        if not len(self):
            return "{} dictionary with 0 objects".format(self.__class__.__name__)
        elif len(self) > 20:
            return (
                "{} dictionary with {} objects, including:"
                "{}\nUse `list(this object)` to get the complete list."
            ).format(
                self.__class__.__name__,
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted(self.data)[:10]]),
            )
        else:
            return ("{} dictionary with {} object(s):{}").format(
                self.__class__.__name__,
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted(self.data)]),
            )

    __repr__ = lambda x: str(x)

    def __delitem__(self, name):
        del self.data[name]
        self.flush()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __hash__(self):
        return hash(self.data)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def serialize(self, filepath=None):
        """Method to do the actual serialization. Can be replaced with other serialization formats.

        Args:
            * *filepath* (str, optional): Provide an alternate filepath (e.g. for backup).

        """
        with atomic_open(filepath or self.filepath, "w") as f:
            f.write(JsonWrapper.dumps(self.pack(self.data)))

    def deserialize(self):
        """Load the serialized data. Can be replaced with other serialization formats."""
        return self.unpack(JsonWrapper.load(self.filepath))

    def pack(self, data):
        """Transform the data, if necessary. Needed because JSON must have strings as dictionary keys."""
        return data

    def unpack(self, data):
        """Return serialized data to true form."""
        return data

    def random(self):
        """Return a random key."""
        if not self.data:
            return None
        else:
            return random.choice(list(self.data.keys()))

    def backup(self):
        """Write a backup version of the data to the ``backups`` directory."""
        filepath = os.path.join(
            self.dirpath, "backups", self.filename + ".%s.backup" % int(time())
        )
        self.serialize(filepath)


class PickledDict(SerializedDict):
    """Subclass of ``SerializedDict`` that uses the pickle format instead of JSON."""

    def serialize(self):
        with atomic_open(self.filepath, "wb") as f:
            pickle.dump(self.pack(self.data), f, protocol=4)

    def deserialize(self):
        try:
            return self.unpack(pickle.load(open(self.filepath, "rb")))
        except ImportError:
            TEXT = "Pickle deserialization error in file '%s'" % self.filepath
            raise PickleError(TEXT)
