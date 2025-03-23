import random
import yaml

from copy import deepcopy

from .animation import Animation
from .containers import BaseContainer


class Chest:
    def __init__(self, chest_type, structure_config, item_config, background='brick_wall_small'):
        self.structure = structure_config
        self.item_config = item_config
        self.name = self.structure['chests'][chest_type]['name']
        self.type = chest_type
        self.image = self.structure['chests'][chest_type]['image']
        self.item_types = self.structure['chests'][chest_type]["item_types"] 
        self.items = BaseContainer(20, locked=True)
        self.locked = True 
        self.opens_with = self.structure['chests'][chest_type]['opens_with']
        self.secret = self.load_secret()
        self.secret_type = 'key'
        self.background = background
        self.animation = None
        self.load_animation()
        self.generate_items()

    def interface(self, command, item=None):

        commands = {
            'pageup': lambda direction: None,
            'pagedown': lambda direction: None,
            'up': self.change_selected_item,
            'down': self.change_selected_item,
            'left': self.change_selected_item,
            'right': self.change_selected_item,
        }

        commands.get(command, lambda direction: None)(command)

    def get_interface_options(self):
        if self.locked:
            return {'u': 'Unlock', 'x': 'eXit'}
        else:
            return {'u': 'Use', 'r': 'Remove', 'e': 'Equip', 'x': 'eXit'}

    def load_secret(self):
        if self.opens_with == 'key':
            return 'key'

    def get_secret_type(self):
            return self.secret_type

    def load_animation(self):
        with open(f'animations/unlock_chest.yml', 'r') as infile:
            unlock_chest_animation = yaml.safe_load(infile)

        with open(f'animations/images/{self.background}.img', 'r') as wall:
            background = wall.read()

        frames = []
        for image in unlock_chest_animation['frames']:
            with open(f'animations/images/{image}.img', 'r') as i:
                frames.append(i.read())
        self.animation = Animation(frames, frame_times=unlock_chest_animation['frame_times'])
        self.animation.build_scene(background, unlock_chest_animation['positions'])

    def update_image(self):
        if not self.items:
            self.image = self.structure['chests'][self.type]['image_empty']
        elif not self.locked:
            self.image = self.structure['chests'][self.type]['image_open']
        else:
            self.image = self.structure['chests'][self.type]['image']

    def generate_items(self):
        for item_type in self.item_types:
            num_items = random.choice([1, 1, 2, 2, 3])
            items = list(self.item_config[item_type].keys())
            for item in set(random.choices(items, k=num_items)):
                self.items.add_item(deepcopy(self.item_config[item_type][item]))
        self.update_image()

    def unlock(self, key):
        if self.locked and key:
            if key.get('id') == 'key_1':
                self.locked = False
                self.items.unlock()
                self.animation.play_animation()
                self.update_image()

    def view_items(self):
        print(f"{self.name}:")
        if self.locked:
            print(self.animation.get_frames()[0])
        else:
            self.items.view_items()
             

    def get_item_list(self):
        return self.items.get_item_list()

    def change_selected_item(self, direction):
        self.items.change_selected_item(direction=direction)

    def get_selected_item(self):
        return self.items.get_selected_item()

    def remove_selection_box(self):
        self.items.remove_selection_box()

    def add_item(self, item):
        self.items.add_item(item)

    def remove_selected_item(self):
        item = self.items.remove_selected_item()
        self.update_image()
        return item

    def is_empty(self):
        return self.items.is_empty()
