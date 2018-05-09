from os.path import exists

_BACKGROUND_IMAGE = b"\x01"
_BACKGROUND = b"\x02"
_OBJECT = b"\x03"
_UNDESTROYABLE_OBJECT = b"\x04"
_UNMOVABLE_OBJECT = b"\x05"


#class BackgroundSprite(sprite.Sprite):
#class ObjectSprite(sprite.Sprite):
#class UndestroyableObject(sprite.Sprite):
#class UnmovableBackground(sprite.Sprite):

class BinaryMapFile:

    def __init__(self, filename, record_size):
        self.__record_size = record_size + 1 # with state byte
        mode = "w+b" if not exists(filename) else "r+b"
        self.__fh = open(filename, mode)