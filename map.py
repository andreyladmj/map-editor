import pickle
import random
import struct
from os import scandir, listdir

from PIL import Image
from cocos import sprite, layer
import cocos.collision_model as cm
from os.path import join

from cocos.director import director
from copy import copy

from cocos.sprite import Sprite
from pyglet.image import TextureRegion

from game.map.BinaryMapFile import BinaryMapFile
from game.map.utils import generate_image

blockSize = 32


class Map(layer.Layer):
    def __init__(self):
        super().__init__()
        self.collisions = cm.CollisionManagerBruteForce()
        self.background = None
        self.generate_new_map()

    def addBrick(self, x, y, spriteBlock):
        x = x // blockSize * blockSize
        y = y // blockSize * blockSize

        if isinstance(spriteBlock, str):
            spriteObj = Sprite(spriteBlock)
        else:
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
        #_MAP_STRUCT = struct.Struct("<8s30sid")
        #file = BinaryMapFile('assets/map.bin', _MAP_STRUCT.size)
        #c = TextureRegion()

        for i in self.collisions.objs:
            #print(i.image, i.position, i.scale, i.rotation)
            print(i, i._animation)
            #print(dir(i))

    def load_map(self):
        with open('assets/map.pickle', 'rb') as handle:
            self = pickle.load(handle)

    def load_background(self, src):
        exists_background = bool(self.background)
        self.background = Sprite(src)
        self.background.position = (self.background.width/2, self.background.height/2)

        if not exists_background:
            self.add(self.background)

    def generate_new_map(self):
        block_size = 32

        self.load_background("assets/image.png")

        w, h = self.background.width, self.background.height
        top_wall = ['assets/objects/226.jpg','assets/objects/227.jpg']
        side_wall = ['assets/objects/220.jpg','assets/objects/221.jpg']

        for i in range(w//block_size):
            self.addBrick(i*32, 0, random.choice(top_wall))
            self.addBrick(i*32, h-block_size/2, random.choice(top_wall))

        for i in range(h//block_size):
            self.addBrick(0, i*32, random.choice(side_wall))
            self.addBrick(w-block_size/2, i*32, random.choice(side_wall))


class Point():
    def __init__(self, x, y):
        self.cshape = cm.AARectShape((x,y), 2, 2)