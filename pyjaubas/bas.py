"""
Implementation of Nintendo's JAudio Sound Animation data format (BAS) that provides methods to construct, serialize,
deserialize and manipulate such data. The data is laid out in a simple list of sound entries and playback information.
Sounds actually use a special sound ID number. To label these IDs, lookup tables are provided for some games.
"""

__all__ = [
    "JAUSoundIdTable", "SuperMarioGalaxy1SoundTable", "SuperMarioGalaxy2SoundTable", "JAUSoundAnimationSound",
    "JAUSoundAnimation", "from_buffer", "pack_buffer", "from_file", "write_file", "from_json", "dump_json"
]

import json
import os
import struct


# ----------------------------------------------------------------------------------------------------------------------
# Sound ID lookup table implementations
# ----------------------------------------------------------------------------------------------------------------------
class JAUSoundIdTable:
    def __init__(self, lookup_file_path):
        """
        Constructs a new sound lookup table using the file of known sound names and IDs. Each line corresponds to one
        name-ID pair where the components are divided by a single comma. This raises a FileNotFoundError if the lookup
        file does not exist.

        :param lookup_file_path: the file path containing the known sound names.
        :raises FileNotFoundError: when the lookup file cannot be found.
        """
        self._lookup_ = dict()

        if os.path.exists(lookup_file_path):
            for field in open(lookup_file_path, "r", encoding="latin1").readlines():
                sound_name, sound_id_str = field.strip("\r\n").split(",")
                self._lookup_[sound_name] = int(sound_id_str)
        else:
            raise FileNotFoundError(f"Lookup names file \"{lookup_file_path}\" cannot be found!")

    def find_name(self, sound_id: int) -> str:
        """
        Retrieves the proper sound label name for the given sound ID if it exists. Otherwise, a KeyError will be raised.

        :param sound_id: the sound ID to search for.
        :return: the sound label name if it exists.
        :raises KeyError: when no sound label name could be found.
        """
        for name, index in self._lookup_.items():
            if index == sound_id:
                return name
        raise KeyError

    def find_id(self, sound_name: str) -> int:
        """
        Retrieves the sound ID for the given sound label name.

        :param sound_name: the sound label name.
        :return: the sound ID.
        """
        return self._lookup_[sound_name]


class SuperMarioGalaxy1SoundTable(JAUSoundIdTable):
    """A sound lookup table implementation for Super Mario Galaxy."""

    def __init__(self):
        """Constructs a new sound lookup table using the known names from Super Mario Galaxy."""
        super().__init__(os.path.join(os.path.dirname(__file__), "lookup_supermariogalaxy1.txt"))


class SuperMarioGalaxy2SoundTable(JAUSoundIdTable):
    """A sound lookup table implementation for Super Mario Galaxy 2."""

    def __init__(self):
        """Constructs a new sound lookup table using the known names from Super Mario Galaxy 2."""
        super().__init__(os.path.join(os.path.dirname(__file__), "lookup_supermariogalaxy2.txt"))


# ----------------------------------------------------------------------------------------------------------------------
# JAudio Sound Animation implementation
# ----------------------------------------------------------------------------------------------------------------------
class JAUSoundAnimationSound:
    """An individual sound entry of a sound animation that specifies how a sound is played."""

    # Structures for parsing and packing
    __STRUCT_BE__ = struct.Struct(">I3fI6B6x")  # Big-endian
    __STRUCT_LE__ = struct.Struct("<I3fI6B6x")  # Little-endian

    def __init__(self):
        """Creates a new sound animation entry with the default values and no specific sound label."""
        self.sound = ""
        self.start_frame = 0.0
        self.unk8 = 0.0
        self.pitch = 1.0
        self.flags = 0
        self.volume = 127
        self.pitch_factor = 0
        self.unk16 = 0
        self.pan = 64
        self.volume_factor = 0
        self.unk19 = 0

    def __repr__(self):
        """Implements "repr(`self`)"."""
        return self.sound

    def _unpack_(self, data, off: int, is_big_endian: bool, lookup: JAUSoundIdTable):
        """
        Unpacks the sound's information from the specified buffer.

        :param data: the buffer.
        :param off: the offset into the buffer.
        :param is_big_endian: the endianness of the data.
        """
        strct = self.__STRUCT_BE__ if is_big_endian else self.__STRUCT_LE__
        sound_id, self.start_frame, self.unk8, self.pitch, self.flags, self.volume, self.pitch_factor, self.unk16,\
        self.pan, self.volume_factor, self.unk19 = strct.unpack_from(data, off)

        self.sound = lookup.find_name(sound_id)

    def _pack_(self, data, off: int, is_big_endian: bool, lookup: JAUSoundIdTable):
        """
        Packs the sound's information into the specified buffer.

        :param data: the buffer.
        :param off: the offset into the buffer.
        :param is_big_endian: the endianness of the data.
        """
        strct = self.__STRUCT_BE__ if is_big_endian else self.__STRUCT_LE__
        strct.pack_into(data, off, lookup.find_id(self.sound), self.start_frame, self.unk8, self.pitch, self.flags,
                        self.volume, self.pitch_factor, self.unk16, self.pan, self.volume_factor, self.unk19)


class JAUSoundAnimation(list):
    __STRUCT_BE__ = struct.Struct(">H2B4x")
    __STRUCT_LE__ = struct.Struct("<H2B4x")

    def __init__(self, lookup: JAUSoundIdTable):
        super().__init__()
        self._lookup_ = lookup
        self.unk2 = 0
        self.unk3 = 0

    def _unpack_(self, data, off: int, is_big_endian: bool):
        strct = self.__STRUCT_BE__ if is_big_endian else self.__STRUCT_LE__
        num_entries, self.unk2, self.unk3 = strct.unpack_from(data, off)
        off += 8

        for _ in range(num_entries):
            sound = JAUSoundAnimationSound()
            sound._unpack_(data, off, is_big_endian, self._lookup_)
            self.append(sound)
            off += 32

    def makebin(self, is_big_endian: bool) -> bytes:
        buffer = bytearray(8 + len(self) * 32)
        strct = self.__STRUCT_BE__ if is_big_endian else self.__STRUCT_LE__
        strct.pack_into(buffer, 0, len(self), self.unk2, self.unk3)

        off_tmp = 8

        for sound in self:
            sound._pack_(buffer, off_tmp, is_big_endian, self._lookup_)
            off_tmp += 32

        return bytes(buffer)


# ----------------------------------------------------------------------------------------------------------------------
# Helper I/O functions
# ----------------------------------------------------------------------------------------------------------------------
def from_buffer(lookup: JAUSoundIdTable, buffer, offset: int, big_endian: bool = True) -> JAUSoundAnimation:
    soundanm = JAUSoundAnimation(lookup)
    soundanm._unpack_(buffer, offset, big_endian)
    return soundanm


def pack_buffer(soundanm: JAUSoundAnimation, big_endian: bool = True) -> bytes:
    return soundanm.makebin(big_endian)


def from_file(lookup: JAUSoundIdTable, file_path: str, big_endian: bool = True) -> JAUSoundAnimation:
    soundanm = JAUSoundAnimation(lookup)
    with open(file_path, "rb") as f:
        soundanm._unpack_(f.read(), 0, big_endian)
    return soundanm


def write_file(soundanm: JAUSoundAnimation, file_path: str, big_endian: bool = True):
    buffer = soundanm.makebin(big_endian)

    with open(file_path, "wb") as f:
        f.write(buffer)
        f.flush()


def dump_json(soundanm: JAUSoundAnimation, file_path: str):
    dumped = {
        "unk2": soundanm.unk2,
        "unk3": soundanm.unk3,
        "sounds": [sound.__dict__ for sound in soundanm]
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dumped, f, indent=4, ensure_ascii=False)
        f.flush()


def from_json(lookup: JAUSoundIdTable, file_path: str) -> JAUSoundAnimation:
    with open(file_path, "r") as f:
        jsondata = json.load(f)

    soundanm = JAUSoundAnimation(lookup)
    soundanm.unk2 = jsondata["unk2"]
    soundanm.unk3 = jsondata["unk3"]

    for sound_entry in jsondata["sounds"]:
        sound = JAUSoundAnimationSound()
        sound.sound = sound_entry["start_frame"]
        sound.unk8 = sound_entry["unk8"]
        sound.pitch = sound_entry["pitch"]
        sound.flags = sound_entry["flags"]
        sound.volume = sound_entry["volume"]
        sound.pitch_factor = sound_entry["pitch_factor"]
        sound.unk16 = sound_entry["unk16"]
        sound.pan = sound_entry["pan"]
        sound.volume_factor = sound_entry["volume_factor"]
        sound.unk19 = sound_entry["unk19"]
        soundanm.append(sound)

    return soundanm
