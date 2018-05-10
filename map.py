import pickle
import random
import struct
from cocos import sprite, layer
import cocos.collision_model as cm
from os.path import join, isfile

from copy import copy

from cocos.sprite import Sprite

from BinaryMapFile import BinaryMapFile
from palitra import CocosSprite, UndestroyableObject
from utils import generate_image

blockSize = 32
MAP_STRUCT = struct.Struct("<25s30sii")

class Map(layer.Layer):
    def __init__(self):
        super().__init__()
        self.collisions = cm.CollisionManagerBruteForce()
        self.background = None

        if not self.load_map():
            self.generate_new_map()

    def addBrick(self, x, y, spriteBlock):
        x = x // blockSize * blockSize
        y = y // blockSize * blockSize

        spriteObj = copy(spriteBlock)

        spriteObj.position = (x, y)
        spriteObj.cshape = cm.AARectShape(spriteObj.position, spriteObj.width//2, spriteObj.height//2)

        if self.collisions.objs_colliding(spriteObj):
            return

        self.collisions.add(spriteObj)
        self.add(spriteObj, z=2)

    def removeBrick(self, x, y):
        x = x // blockSize * blockSize
        y = y // blockSize * blockSize
        point = Point(x, y)
        obj = self.collisions.any_near(point, 1)
        if obj:
            self.collisions.remove_tricky(obj)
            self.remove(obj)

    def generate_new_background(self):
        generate_image()

    def save_map(self):
        with BinaryMapFile('assets/map.bin', MAP_STRUCT.size) as file:
            file.clear()

            for block in self.collisions.objs:
                x, y = block.position
                map_struct = MAP_STRUCT.pack(
                    block.__class__.__name__.encode("utf8"),
                    block.src.encode("utf8"),
                    int(x),
                    int(y)
                )
                file.append(map_struct)

        return True

    def load_map(self):
        module = __import__('palitra')

        if not isfile('assets/map.bin'):
            return False

        with BinaryMapFile('assets/map.bin', MAP_STRUCT.size) as file:
            self.load_background("assets/image.png")
            for item in file:
                CLS, SRC, X, Y = range(4)
                block = MAP_STRUCT.unpack(item)
                cls = block[CLS].decode("utf8").rstrip("\x00")
                src = block[SRC].decode("utf8").rstrip("\x00")

                class_ = getattr(module, cls)
                instance = class_(src)
                self.addBrick(block[X], block[Y], instance)

    def load_background(self, src):
        exists_background = bool(self.background)
        self.background = Sprite(src)
        self.background.position = (self.background.width/2, self.background.height/2)

        if not exists_background:
            self.add(self.background)

    def generate_new_map(self):
        self.load_background("assets/image.png")

        w, h = self.background.width, self.background.height
        top_wall = [
            UndestroyableObject('assets/objects/226.jpg'),
            UndestroyableObject('assets/objects/227.jpg')
        ]
        side_wall = [
            UndestroyableObject('assets/objects/220.jpg'),
            UndestroyableObject('assets/objects/221.jpg'),
        ]

        for i in range(w//blockSize):
            self.addBrick(i*blockSize, 0, random.choice(top_wall))
            self.addBrick(i*blockSize, h-blockSize/2, random.choice(top_wall))

        for i in range(h//blockSize):
            self.addBrick(0, i*blockSize, random.choice(side_wall))
            self.addBrick(w-blockSize/2, i*blockSize, random.choice(side_wall))


class Point():
    def __init__(self, x, y):
        self.cshape = cm.AARectShape((x,y), 2, 2)