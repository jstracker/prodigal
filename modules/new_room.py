import random
import yaml

import modules.animation as animation
from copy import deepcopy
from pathlib import Path
#from modules.animation import Animation
from modules.new_chests import Chest
from modules.containers import BaseContainer

from time import sleep

class Room:

    def __init__(self, structure_config, items_config, limits, coordinates, room_positions, structure_paths, room_theme='default'):
        self.structure = structure_config
        self.room_config = self.structure['room_themes'][room_theme]
        self.items_config = items_config
        self.limits = limits
        self.name = self.room_config['name']
        self.description = self.room_config['description']
        self.screen_background = random.choice(self.room_config['walls'])
        self.floor_background = random.choice(self.room_config['floors'])
        self.coordinates = coordinates
        self.structure_paths = structure_paths
        self.items = BaseContainer(10, self.name) 

        self.directions = ['north', 'south', 'east', 'west', 'up', 'down']
        x, y, z = self.coordinates
        self.adjacent_positions = {
            'north': (x, y, z + 1),
            'south': (x, y, z - 1),
            'east': (x + 1, y, z),
            'west': (x - 1, y, z),
            'up': (x, y + 1, z),
            'down': (x, y - 1, z),
        }

        self.opposite_directions = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
            'up': 'down',
            'down': 'up',
        }

        self.chest = None
        self.npc = None
        self.screen_views = {}
        self.exits = {}
        self.__post_init__(room_positions)

    def __post_init__(self, room_positions):
        self.generate_chest()
        self.generate_npc()
        self.build_room(room_positions)
        self.create_screen_image()
        self.generate_room_items()
        self.create_map_image()

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
            #self.exits[direction] = self.structure['build'][passage["opens_to"]]
            self.exits[direction]['blocking_image'] = None
            self.exits[direction]['solid'] = False
            self.create_map_image()
            self.create_screen_image()
            print(f"{passage['name']} opened with {tool['name']}")
        elif passage['solid'] and passage['pass_with']:
            return "You must use a {} to pass through a {}".format(' or '.join(passage['pass_with']), passage['name'])
        elif passage['solid']:
            return f"You can not pass through this {passage['name']}"

    def build_room(self, room_positions):
        x, y, z = self.coordinates
        directions = ['north', 'south', 'east', 'west', 'up', 'down']

        # Get the exit types for adjacent rooms so they can be matched
        room_exits = {
            direction: room_positions[self.adjacent_positions[direction]].exits.get(self.opposite_directions[direction])
            for direction in directions
            if room_positions.get(self.adjacent_positions[direction])
        }
        
        for exit_direction in directions:
            possible_exits = {
                k: v
                for k, v in self.structure['build'].items()
                if exit_direction in v['directions']
                and k in self.room_config['builds']
                # maybe move this so new room can be forced into out of bounds area if needed
                and all(
                    [
                        self.limits['min'][axis] <= self.adjacent_positions[exit_direction][axis] <= self.limits['max'][axis]
                        for axis in range(3)
                    ]
                )
            }
            weights = [possible_exit['weight'] for possible_exit in possible_exits.values()]
            # Force more open pathways if the number got too low
            """
            if self.structure_paths <= 2 and possible_exits:
                open_possible_exits = {k: v for k, v in possible_exits.items() if not v['solid']}
                self.exits[exit_direction] = (
                    room_exits.get(exit_direction) or deepcopy(self.structure['build'][random.choice(list(open_possible_exits.keys()))])
                )
            elif possible_exits:
                self.exits[exit_direction] = (
                    room_exits.get(exit_direction) or deepcopy(self.structure['build'][random.choices(list(possible_exits.keys()), weights=weights)[0]])
                )
            elif exit_direction in ['up', 'down']:
                self.exits[exit_direction] = deepcopy(self.structure['build']['floor'])
            else:
                self.exits[exit_direction] = deepcopy(self.structure['build']['wall'])
            """

            if room_exit := room_exits.get(exit_direction):
                self.exits[exit_direction] = room_exit
                continue
            elif self.structure_paths <= 2 and possible_exits:
                open_possible_exits = {k: v for k, v in possible_exits.items() if not v['solid']}
                self.exits[exit_direction] = deepcopy(self.structure['build'][random.choice(list(open_possible_exits.keys()))])
            elif possible_exits:
                self.exits[exit_direction] = deepcopy(self.structure['build'][random.choices(list(possible_exits.keys()), weights=weights)[0]])
            elif exit_direction in ['up', 'down']:
                self.exits[exit_direction] = deepcopy(self.structure['build']['floor'])
            else:
                self.exits[exit_direction] = deepcopy(self.structure['build']['wall'])
            self.exits[exit_direction]['screen_image'] = [random.choice( self.exits[exit_direction]['screen_image']) if  self.exits[exit_direction]['screen_image'] else None]
            self.exits[exit_direction]['blocking_image'] = [random.choice( self.exits[exit_direction]['blocking_image']) if  self.exits[exit_direction]['blocking_image'] else None]


    def generate_chest(self):
        chest_weights = [1, *[chest_type['weight'] for chest_type in self.structure['chests'].values() if chest_type['id'] in self.room_config['chests']]]
        if len(chest_weights) > 1 and (chest_type := random.choices([None, *list(self.structure['chests'].keys())], weights=chest_weights, k=1)[0]):
            self.chest = Chest(chest_type, self.structure, self.items_config)

    def generate_npc(self):
        """
        npc_weights = [1, *[npc_type['weight'] for npc_type in self.structure['npcs'].values() if npc_type['id'] in self.room_config['npcs']]]
        if len(npc_weights) > 1 and (npc_type := random.choices([None, *list(self.structure['npcs'].keys())], weights=npc_weights, k=1)[0]):
        """
        if self.room_config['npcs']:
            npcs = []
            npc_weights = []
            for npc_type in self.room_config['npcs']:
                npcs.append(npc_type)
                npc_weights.append(self.structure['npcs'][npc_type]['weight'])
            #weights = [1, *npc_weights]
            #if npc_type := random.choices([None, *npcs], weights=weights, k=1)[0]:
            if npc_type := random.choices(npcs, weights=npc_weights, k=1)[0]:
                self.npc = self.structure['npcs'][npc_type]

    def generate_room_items(self):
        for item_type in self.room_config['item_types']:
            weights = [item['weight'] for item in self.items_config[item_type].values()]
            num_items = random.choice([0, 0, 0, 0, 1])
            items = list(self.items_config[item_type].keys())
            for item in set(random.choices(items, weights=weights, k=num_items)):
                self.items.add_item(deepcopy(self.items_config[item_type][item]))

    def get_item_list(self):
        return self.items.get_item_list()

    def create_map_image(self):

        images = {
            'north_wall': self.structure['build']['wall']['north']['map_image'],
            'south_wall': self.structure['build']['wall']['south']['map_image'],
            'east_wall': self.structure['build']['wall']['east']['map_image'],
            'west_wall': self.structure['build']['wall']['west']['map_image'],
            'chest': self.chest.map_image if self.chest else ' ',
            'room_id': self.room_config['map_image'] or ' '
        }

        exit_image = {}
        for direction, room_exit in self.exits.items():
            if room_exit['id'] == 'wall':
                exit_image[direction] = room_exit[direction]['map_image']
            elif room_exit['id'] == 'secret_door':
                exit_image[direction] = images[f"{direction}_wall"]
            else:
                exit_image[direction] = room_exit['map_image'] 

        self.map_image = [
            "{1}{1}{1}{1}{0}{1}{1}{1}{1}".format(exit_image.get('north', images['north_wall']), images['north_wall']),
            "{}{} {}   {}{}".format(images['west_wall'], images['chest'], images['room_id'], exit_image.get('up'), images['east_wall']),
            "{}       {}".format(images['west_wall'], images['east_wall']),
            "{}       {}".format(exit_image.get('west', images['west_wall']), exit_image.get('east', images['east_wall'])),
            "{}       {}".format(images['west_wall'], images['east_wall']),
            "{}      {}{}".format(images['west_wall'], exit_image.get('down'), images['east_wall']),
            "{1}{1}{1}{1}{0}{1}{1}{1}{1}".format(exit_image.get('south', images['south_wall']), images['south_wall']),
        ]

    def create_screen_image(self):
        stairs = {
            'upstairs': random.choice(upstairs) if (upstairs := self.exits['up']['screen_image']) else [],
            'downstairs': random.choice(downstairs) if (downstairs := self.exits['down']['screen_image']) else []
        }
        chest = None
        npc = None
        if self.chest:
            chest = [animation.get_images(self.chest.screen_image, image_type='chests', view='closed')[0], [30, 0], 0]
        if self.npc:
            npc = [animation.get_images(self.npc['screen_image'][0])[0], self.npc['screen_image'][1], self.npc['screen_image'][2]]
        for exit_dir in ['north', 'south', 'east', 'west']:
            door = self.exits[exit_dir]
            door_image = random.choice(door['screen_image']) if door['screen_image'] else None
            door_block = random.choice(door['blocking_image']) if door['blocking_image'] else None
            self.screen_views[exit_dir] = WallImage(
                self.room_config['screen_locations'],
                exit_dir,
                self.screen_background,
                self.floor_background,
                door=door_image,
                door_block=door_block,
                stairs=stairs,
                chest=chest,
                npc=npc,
            )
            stairs.clear()
            chest = None
            npc = None

        def get_screen_views(self):
            return self.screen_views


class WallImage:
    def __init__(self, screen_locations, direction, bg_name, fl_name, door=None, door_block=None, chest=None, npc=None, stairs=None):
        self.screen_locations = screen_locations
        self.direction = direction 
        background = animation.get_images(bg_name, image_type='backgrounds', size='full')[0]
        self.door = door
        self.animations = []
        self.adjacent_room_coordinates = []
        door_image = []
        if door:
            door_image.append([animation.get_images(self.door[0], image_type='doors', view='closed')[0], self.door[1], self.door[2]])
            if door_block: 
                door_image.append([animation.get_images(door_block[0])[0], door_block[1], door_block[2]])

        self.chest = chest
        self.npc = npc

        self.top_left = []
        self.top_center = []
        self.top_right = []
        self.bottom_left = []
        self.bottom_center = door_image or []
        self.bottom_right = []
        self.foreground = []

        if direction in ['north', 'south']:
            fl_view = 'horizontal_view'
        else:
            fl_view = 'vertical_view'
        self.floor = animation.get_images(fl_name, image_type='floors', size='full', view=fl_view)[0]

        self.background = animation.combine_images(background, [[self.floor, (0, 0), 0]])

        if chest:
            self.bottom_left.append(chest)
        if npc:
            self.foreground.append(npc)

        stair_images = {}
        if stairs and (upstairs := stairs.get('upstairs')):
            self.top_right.append([animation.get_images(upstairs[0], image_type='stairs', view='up')[0], upstairs[1], upstairs[2]])
        if stairs and (downstairs := stairs.get('downstairs')):
            self.bottom_right.append([animation.get_images(downstairs[0], image_type='stairs', view='down')[0], downstairs[1], downstairs[2]])

        for screen_location in self.screen_locations.keys():
            if not getattr(self, screen_location):
                if images := self.screen_locations[screen_location]:
                    chosen, pos, level = random.choice(images)
                    image_list = [[image, pos, level] for image in animation.get_images(chosen)]
                    setattr(self, screen_location, image_list)

        self.build_screen()

    def build_screen(self):
        self.screen_image = animation.combine_images(
            self.background, [
                x for x in [
                    *self.top_left,
                    *self.bottom_left,
                    *self.top_right,
                    *self.bottom_right,
                    *self.top_center,
                    *self.bottom_center,
                    *self.foreground,
                ]
                if x
                ]
            )

    def change_screen(self, screen_section, image):
        setattr(self, screen_section, image)

    def get_screen_image(self):
        return self.screen_image

    def print_wall(self):
        print(self.screen_image)
