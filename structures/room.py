import random
import yaml

from copy import deepcopy
from pathlib import Path
from modules.animation import Animation
from modules.chests import Chest
from modules.containers import BaseContainer

from time import sleep

class Room:

    def __init__(self, structure_config, items_config, coordinates, room_positions, structure_paths):
        self.structure = structure_config
        self.items_config = items_config
        self.name = "Room"
        self.description = "A normal looking room"
        self.items = BaseContainer(10, self.name) 
        self.item_types = ["food", "items", "tools", "keys"]
        self.chest = None
        self.coordinates = coordinates
        self.screen_views = {}
        self.screen_background = 'brick_wall_full.img'
        self.exits = {}
        self.open_paths = 0
        self.structure_paths = structure_paths
        self.build_room(room_positions)

    def __post_init__(self, kwargs):
        pass

    def __repr__(self):
        room_output = f"{self.name}\n{self.description}"
        return room_output

    def __str__(self):
        room_output = f"{self.name}\n{self.description}"
        return room_output

    def get_interface_options(self):
        return {'u': 'Use', 'r': 'Remove', 'e': 'Equip', 'l': 'Look', 'x': 'eXit'}

    def get_exit_options(self):
        return '\n'.join([f"{direction} {exit_type['name']}" for direction, exit_type in self.exits.items()])

    def get_exits(self):
        return self.exits

    def open_room_passage(self, direction, tool=None):
        passage = self.exits[direction]
        if passage['solid'] and tool and tool['id'] in passage['pass_with']:
            self.exits[direction] = self.structure['build'][passage["opens_to"]]
            self.create_map_image()
            print(f"{passage['name']} opened with {tool['name']}")
        #elif passage['solid'] and passage['pass_with']:
        #    print("You must use a {} to pass through a {}".format(' or '.join(passage['pass_with']), passage['name']))
        #elif passage['solid']:
        #    print(f"You can not pass through a {passage['name']}")

    def build_room(self, room_positions):
        x, y, z = self.coordinates
        directions = ['north', 'south', 'east', 'west', 'up', 'down']

        positions = {
            'north': (x, y, z + 1),
            'south': (x, y, z - 1),
            'east': (x + 1, y, z),
            'west': (x - 1, y, z),
            'up': (x, y + 1, z),
            'down': (x, y - 1, z),
        }

        opposites = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
            'up': 'down',
            'down': 'up',
        }

        chest_weights = [0, *[chest_type['weight'] for chest_type in self.structure['chests'].values()]]
        if chest_type:= random.choices([None, *list(self.structure['chests'].keys())], weights=chest_weights, k=1)[0]:
            self.chest = Chest(chest_type, self.structure, self.items_config)

        room_exits = {
            direction: room_positions[positions[direction]].exits.get(opposites[direction])
            for direction in directions
            if room_positions.get(positions[direction])
        }
        
        for exit_direction in directions:
            possible_exits = {k: v for k, v in self.structure['build'].items() if exit_direction in v['directions']}
            weights = [possible_exit['weight'] for possible_exit in possible_exits.values()]
            if self.structure_paths <= 1:
                open_possible_exits = {k: v for k, v in possible_exits.items() if not v['solid']}
                self.exits[exit_direction] = (
                    room_exits.get(exit_direction) or self.structure['build'][random.choice(list(open_possible_exits.keys()))] 
                )
            else:
                self.exits[exit_direction] = (
                    room_exits.get(exit_direction) or self.structure['build'][random.choices(list(possible_exits.keys()), weights=weights)[0]]
                )

        self.open_paths += sum([1 for room_exit in self.exits.values() if not room_exit['solid']]) - 1

        self.create_screen_image()
        self.generate_room_items()
        self.create_map_image()

    def generate_room_items(self):
        for item_type in self.item_types:
            weights = [item['weight'] for item in self.items_config[item_type].values()]
            num_items = random.choice([0, 0, 0, 0, 1])
            items = list(self.items_config[item_type].keys())
            for item in set(random.choices(items, weights=weights, k=num_items)):
                self.items.add_item(deepcopy(self.items_config[item_type][item]))

    def get_item_list(self):
        return self.items.get_item_list()

    def create_map_image(self):

        images = {
            'north_wall': self.structure['build']['wall']['north']['image'],
            'south_wall': self.structure['build']['wall']['south']['image'],
            'east_wall': self.structure['build']['wall']['east']['image'],
            'west_wall': self.structure['build']['wall']['west']['image'],
            'chest': self.chest.image if self.chest else self.structure['build']['floor']['image'],
        }

        exit_image = {}
        for direction, room_exit in self.exits.items():
            if room_exit['id'] == 'wall':
                exit_image[direction] = room_exit[direction]['image']
            elif room_exit['id'] == 'secret_door':
                exit_image[direction] = images[f"{direction}_wall"]
            else:
                exit_image[direction] = room_exit['image'] 

        self.map_image = [
            "{1}{1}{1}{1}{0}{1}{1}{1}{1}".format(exit_image.get('north', images['north_wall']), images['north_wall']),
            "{}{}     {}{}".format(images['west_wall'], images['chest'], exit_image.get('up'), images['east_wall']),
            "{}       {}".format(images['west_wall'], images['east_wall']),
            "{}       {}".format(exit_image.get('west', images['west_wall']), exit_image.get('east', images['east_wall'])),
            "{}       {}".format(images['west_wall'], images['east_wall']),
            "{}      {}{}".format(images['west_wall'], exit_image.get('down'), images['east_wall']),
            "{1}{1}{1}{1}{0}{1}{1}{1}{1}".format(exit_image.get('south', images['south_wall']), images['south_wall']),
        ]

    def create_screen_image(self):
        with open(f'animations/images/{self.screen_background}', 'r') as infile:
            room_background = infile.read()

        animation = Animation([])

        #for exit_dir, exit_info in self.exits.items():
        for exit_dir in ['north', 'south', 'east', 'west', 'up', 'down']:
            position = self.exits[exit_dir].get('screen_position', [])
            images = []

            if exit_dir == 'up':
                background = self.screen_views['north']
                image_key = 'north'
            elif exit_dir == 'down':
                background = self.screen_views['east']
                image_key = 'south'
            else:    
                background = deepcopy(room_background)
                image_key = exit_dir 

            for screen_image in self.exits[exit_dir].get('screen_image', []):
                with open(f"animations/images/{screen_image}", 'r') as image_file:
                    images.append(image_file.read())
            self.screen_views[image_key] = animation.combine_images(background, images, [position] * len(images))

        if self.chest:                  
            with open(f"animations/images/closed_chest.img", 'r') as image_file:
                image = image_file.read()
                self.screen_views['north'] = animation.combine_images(self.screen_views['north'], [image], [[30,0]])
       


class wall:
    def __init__():
        #self.map_image
        self.screen_image
        self.direction
        self.animations
        self.exit_coordinates
