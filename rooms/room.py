import random
import yaml

from pathlib import Path
from pprint import pprint

with open('rooms/items.yml') as yconfig:
    config = yaml.safe_load(yconfig)

with open('rooms/structures.yml') as yconfig:
    structures = yaml.safe_load(yconfig)


class Structure:
    def __init__(self, start_coordinates=None, max_size=(3, 3, 3)):
        self.structure = structures['castle']
        self.open_paths = 0
        self.max_size = max_size
        self.build_map()
        self.start_coordinates = start_coordinates or (0, 0, 0)
        self.room_positions = {}
        self.add_room(self.start_coordinates)
        self.current_room = self.start_coordinates
        self.update_player_pos()

    def add_room(self, coordinates):
        x, y, z = coordinates
        self.room_positions[coordinates] = Room(coordinates, self.room_positions, self.open_paths)
        self.open_paths += self.room_positions[coordinates].open_paths

    def get_current_room(self):
        return self.room_positions[self.current_room]

    def exit_room(self, direction):
        x, y, z = self.current_room
        direction_coords = {
            'north': (x, y, z + 1),
            'south': (x, y, z - 1),
            'east': (x + 1, y, z),
            'west': (x - 1, y, z),
            'up': (x, y + 1, z),
            'down': (x, y - 1, z),
        }

        path = self.get_current_room().exits[direction]
        if path['solid'] and path['pass_with']:
            print("You must use a {} to pass through a {}".format(' or '.join(path['pass_with']), path['name']))
            return
        elif path['solid']:
            print(f"You can not pass through a {path['name']}")
            return

        new_coordinates = direction_coords[direction]

        if new_coordinates not in self.room_positions.keys():
            self.add_room(new_coordinates)
        old_coords = self.current_room
        self.current_room = new_coordinates
        self.update_player_pos(direction=direction, past_room=old_coords)

    def update_player_pos(self, direction='up', past_room=None):
        player_image = '\u263B'
        player_coords = {
            'north': (5, 3),
            'south': (1, 3),
            'east': (3, 1),
            'west': (3, 5),
            'up': (3, 3),
            'down': (3, 3),
        }
        cur_room_pos = self.room_positions[self.current_room].map_image[player_coords[direction][0]]
        self.room_positions[self.current_room].map_image[
            player_coords[direction][0]
        ] = f"{cur_room_pos[0:player_coords[direction][1] + 1]}{player_image}{cur_room_pos[player_coords[direction][1] + 2:]}"

        if past_room:
            self.room_positions[past_room].map_image = [
                row.replace(player_image, ' ') for row in self.room_positions[past_room].map_image
            ]

    def build_map(self):
        max_x, max_y, max_z = self.max_size
        image = ['\u2591' * 9] * 7
        self.map = [[[image for z in range(max_z)] for y in range(max_y)] for x in range(max_x)]

    def get_map(self, level=None):

        blank_map_image = ['\u2591' * 9] * 7

        m = sorted(self.room_positions.keys(), key=lambda k: [k[1], k[0], k[2]])
        x_coords = [x for x, y, z in m]
        y_coords = [y for x, y, z in m]
        z_coords = [z for x, y, z in m]

        if level == None:
            y_levels = [y for y in range(min(y_coords), max(y_coords) + 1)]
        else:
            y_levels = [level]

        for y in y_levels:
            print(f"level {y}")
            for z in range(max(z_coords), min(z_coords) - 1, -1):
                print(
                    '\n'.join(
                        [
                            ''.join(
                                (
                                    self.room_positions.get((x, y, z)).map_image
                                    if self.room_positions.get((x, y, z))
                                    else blank_map_image
                                )[row]
                                for x in range(min(x_coords), max(x_coords) + 1)
                            )
                            for row in range(7)
                        ]
                    )
                )


class Room:

    def __init__(self, coordinates, room_positions, structure_paths, kwargs=None):
        self.structure = structures['castle']
        self.name = "Name of room"
        self.description = "This is a room"
        self.items = {}
        self.item_types = ["food", "items", "tools"]
        self.chest = None
        self.coordinates = coordinates
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

        chest_weights = [30, *[chest_type['weight'] for chest_type in self.structure['chests'].values()]]
        if chest_type:= random.choices([None, *list(self.structure['chests'].keys())], weights=chest_weights, k=1)[0]:
            self.chest = Chest(chest_type)
        self.generate_room_items()
        self.create_map_image()

    def generate_room_items(self):
        for item_type in self.item_types:
            weights = [item['weight'] for item in config[item_type].values()]
            num_items = random.choice([0, 0, 0, 0, 1])
            items = list(config[item_type].keys())
            self.items.update({item: config[item_type][item] for item in set(random.choices(items, weights=weights, k=num_items))})


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


class Chest:
    def __init__(self, chest_type):
        self.structure = structures['castle']
        self.name = self.structure['chests'][chest_type]['name']
        self.type = chest_type
        self.image = self.structure['chests'][chest_type]['image']
        self.item_types = self.structure['chests'][chest_type]["item_types"] 
        self.items = {}
        self.locked = False 
        self.opens_with = self.structure['chests'][chest_type]['opens_with']
        self.secret = self.load_secret()
        self.add_items()

    def load_secret(self):
        if self.opens_with == 'key':
            return 'key'

    def update_image(self):
        if not self.items:
            self.image = self.structure['chests'][self.type]['image_empty']
        elif not self.locked:
            self.image = self.structure['chests'][self.type]['image_open']
        else:
            self.image = self.structure['chests'][self.type]['image']

    def add_items(self):
        for item_type in self.item_types:
            num_items = random.choice([1, 1, 2, 2, 3])
            items = list(config[item_type].keys())
            self.items.update({item: config[item_type][item] for item in set(random.choices(items, k=num_items))})
        self.update_image()

    def unlock_chest(self, key):
        if self.locked and key == self.secret:
            self.locked = False

    def open_chest(self):
        if not self.locked:
            contents = [item['name'] for item in self.items.values()]
            print(contents)
            return self.items


class Player:
    def __init__(self, name):
        self.name = name
        self.max_health = 100
        self.health = 100
        self.max_magic = 20
        self.magic = 10
        self.money = 0
        self.items = {} 
        self.weapons = []
        self.armor = []
        self.tools = []
        self.left_hand = ''
        self.right_hand = ''
        self.equipped = {'shield': {}, 'weapon': {}, 'armor': {}}
        self.attack = 1
        self.defense = 1
        self.stealth = 5

    def load_structure(self, structure):
        self.structure = structure 

    def attack(self):
        pass

    def defend(self):
        pass

    def action(self, structure):
        pass

    def move(self, structure, direction=''):
        current_room = structure.get_current_room()
        exit_options = current_room.get_exit_options()
        exits = current_room.get_exits()
        print(exit_options)
        #direction = ''
        while direction not in current_room.exits.keys():
            direction = input('move: ').strip()
            if direction == 'exit':
                return
        tool = None
        if current_room.exits[direction]['solid']:
            if current_room.exits[direction]['id'] == 'locked_door' and self.items.get('key', {'num': 0})['num']:
                self.items['key']['num'] -= 1
                tool = self.items['key']
            else:
                print(f"The way is blocked by a {current_room.exits[direction]['name']}")
            current_room.open_room_passage(direction, tool=tool)
        structure.exit_room(direction)

    def add_to_inventory(self, item):
        if item['type'] in ['items', 'food']:
            self.items.setdefault(item['id'], item).setdefault('num', 0)
            self.items[item['id']]['num'] += 1
        elif item['type'] == 'money':
            self.money += item['amount']
        elif item['type'] == 'weapons':
            self.weapons.append(item)
        elif item['type'] == 'armor':
            self.armor.append(item)
        elif item['type'] == 'tools':
            self.tools.append(item)

    def pickup_item(self, structure):
        current_room = structure.get_current_room()
        item = ''
        while item not in list(current_room.items.keys()) and current_room.items:
            item = input(f'Choose item to pick up {list(current_room.items.keys())}: ')
            if item == 'exit':
                return
            elif item in current_room.items.keys():
                self.add_to_inventory(current_room.items.pop(item))
                #self.items.setdefault(item, current_room.items.pop(item)).setdefault('num', 0)
                #self.items[item]['num'] += 1

    def unlock_chest(self, structure):
        current_room = structure.get_current_room()
        chest = current_room.chest
        if not chest.locked:
            print("The chest is already unlocked.")
        elif chest.secret == 'key':
            if self.items.get('key', {'num': 0})['num']:
                chest.unlock_chest('key')
                self.items['key']['num'] -= 1
            else:
                print(f"You need a {chest.opens_with} to open the chest.")

    def open_chest(self, structure):
        current_room = structure.get_current_room()
        chest = current_room.chest
        if chest.locked:
            print(f"The chest is locked. You need a {chest.opens_with}.")
        else:
            chest_items = chest.open_chest()
            for item in [*chest_items.keys()]:
                """
                if chest_items[item]['type'] == 'items':
                    self.items.setdefault(item, chest.items.pop(item)).setdefault('num', 0)
                    self.items[item]['num'] += 1
                elif chest_items[item]['type'] == 'weapons':
                    self.weapons.append(chest.items.pop(item))
                elif chest_items[item]['type'] == 'armor':
                    self.armor.append(chest.items.pop(item))
                """
                self.add_to_inventory(chest.items.pop(item))
        chest.update_image()
        current_room.create_map_image()
        structure.update_player_pos()

    def inventory(self):
        options = ['use', 'equip', 'exit']
        items = '\n\t'.join([f"{values['name']}: {values['num']}" for values in self.items.values()])
        weapons = '\n\t'.join([f"{weapon['name']}: damage={weapon['damage']} durability={weapon['durability']}" for weapon in self.weapons])
        armor = '\n\t'.join([f"{armor['name']}: defense={armor['defense']} durability={armor['durability']}" for armor in self.armor])
        tools = '\n\t'.join([f"{tool['name']}: damage={tool['damage']} durability={tool['durability']}" for tool in self.tools])
        print(f"Money: ${self.money}")
        print(f"Items:\n\t{items}")
        print(f"Tools:\n\t{tools}")
        print(f"Weapons:\n\t{weapons}")
        print(f"Armor:\n\t{armor}")

        option = None
        while option not in options:
            option = input(f"Options {options}: ")
            if option == 'exit':
                return
            if option == 'use':
                usable_items = [item['name'] for item in self.tools + list(self.items.values())]
                usable_items.append('exit')
                item = None 
                while item not in usable_items and usable_items:
                    item = input(f"Use {usable_items}: ")
                    if item.lower() == 'exit':
                        return
                self.use_item(item) 
            if option == 'equip':
                pass

    def equip(self, equipment):
        pass

    def use_item(self, item):
        if item['type']['items']:
            pass
        if item['type']['food']:
            pass
        if item['type']['tool']:
            pass


class Inventory:
    def __init__(self):
        self.money = 0 
        self.items = self.create_slots((10, 2))
        self.tools = self.create_slots((10, 2))
        self.weapons = self.create_slots((10, 2))
        self.armor = self.create_slots((10, 2))
        self.add_item({'name': 'Key', 'type': 'items', 'id': 'key', 'num': 0})
        self.add_item({'name': 'Apple', 'type': 'food', 'id': 'apple', 'num': 0})

    def create_slots(self, size):
        x_size, y_size = size
        return [
            [
                {
                    'up': (x, y + 1),
                    'down': (x, y - 1),
                    'left': (x - 1, y),
                    'right': (x + 1, y),
                    'item': None
                }
                for y in range(y_size)
            ]
            for x in range(x_size)
        ]

    def open_inventory(self):
        item_slot = (0, 0)
        tools_slot = (0, 0)
        weapons_slot = (0, 0)
        armor_slot = (0, 0)

        print('Items:')
        for x in self.items:
            #for y in x:
            #print('\t' + ' '.join([item for y in x for item in y]))
            print([f"{y['item']}-{self.items[y['right'][0]][y['right'][1]]['item']}"  for y in x])
        #pprint(f"{self.money=}")
        #pprint(f"{self.items=}")
        #pprint(f"{self.tools=}")
        #pprint(f"{self.weapons=}")
        #pprint(f"{self.armor=}")

    def draw_inventory(self):
        pass

    def add_slots(self, num_slots):
        pass

    def add_item(self, item):
        if item['type'] in ['items', 'food']:
            for y in range(len(self.items[0])):
                for x in range(len(self.items)):
                    if not self.items[x][y]['item']:
                        self.items[x][y]['item'] = item
                        return

            #self.items.setdefault(item['id'], item).setdefault('num', 0)
            #self.items[item['id']]['num'] += 1
        elif item['type'] == 'money':
            self.money += item['amount']
        elif item['type'] == 'weapons':
            self.weapons.append(item)
        elif item['type'] == 'armor':
            self.armor.append(item)
        elif item['type'] == 'tools':
            self.tools.append(item)
        pass

    def remove_item(self, item):
        pass


class Battle:
    def __init__(self, player, enemies):
        pass
