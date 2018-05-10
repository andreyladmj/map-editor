import os
from os.path import exists

_BACKGROUND_IMAGE = b"\x01"
_BACKGROUND = b"\x02"
_OBJECT = b"\x03"
_UNDESTROYABLE_OBJECT = b"\x04"
_UNMOVABLE_OBJECT = b"\x05"


class BinaryMapFile:
    def __init__(self, filename, record_size):
        self.__record_size = record_size
        mode = "w+b" if not exists(filename) else "r+b"
        self.__fh = open(filename, mode)

    @property
    def record_size(self):
        "The size of each item"
        return self.__record_size

    @property
    def name(self):
        "The name of the file"
        return self.__fh.name

    def flush(self):
        self.__fh.flush()

    def close(self):
        self.__fh.close()

    def __setitem__(self, index, record):
        """Sets the item at position index to be the given record
        The index position can be beyond the current end of the file.
        """
        assert isinstance(record, (bytes, bytearray)), \
            "binary data required"
        assert len(record) == self.record_size, (
            "record must be exactly {0} bytes".format(
                self.record_size))

        self.__fh.seek(index * self.__record_size)
        self.__fh.write(record)
        self.__fh.flush()

    def __getitem__(self, index):
        """Returns the item at the given index position
        If there is no item at the given position, raises an
        IndexError exception.
        If the item at the given position has been deleted returns
        None.
        """
        self.__seek_to_index(index)
        state = self.__fh.read(1)
        return self.__fh.read(self.record_size)

    def append(self, struct):
        self.__seek_to_end()
        self.__fh.write(struct)
        self.__fh.flush()

    def clear(self):
        self.__fh.truncate()
        self.__fh.seek(0)

    def __seek_to_index(self, index):
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        offset = index * self.__record_size
        if offset >= end:
            raise IndexError("no record at index position {0}".format(
                index))
        self.__fh.seek(offset)

    def __seek_to_end(self):
        self.__fh.seek(0, os.SEEK_END)

    def __len__(self):
        """The number number of record positions.
        This is the maximum number of records there could be at
        present. The true number may be less because some records
        might be deleted. After calling compact() (or
        inplace_compact()), this returns the true number.
        """
        self.__fh.seek(0, os.SEEK_END)
        end = self.__fh.tell()
        return end // self.__record_size

    def __iter__(self):
        self.__fh.seek(0)
        pack = self.__fh.read(self.__record_size)

        while pack:
            yield pack
            pack = self.__fh.read(self.__record_size)

        # for index in range(len(self.__file)):
        #     record = self.__file[index]


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # check on exception
            self.close()
