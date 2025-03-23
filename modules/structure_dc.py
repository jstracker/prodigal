import random

# from .room import Room
# from modules.new_room import Room
from copy import deepcopy
from modules.new_chests import Chest
#from modules.room import Room
import  modules.animation
from modules.save_room import Room
from modules.containers import BaseContainer


class Structure:
    def __init__(self, structure_config, items_config, animations, start_coordinates=None, map_limits=None, entry_theme='default'):
        self.structure = structure_config
        self.items_config = items_config
        self.animations = animations
        self.open_paths = 0
        self.map_limits = map_limits or {'max': (3, 4, 3), 'min': (-1, -4, -4)}
        self.start_coordinates = start_coordinates or (0, 0, self.map_limits['min'][2] - 1)
        self.room_positions = {}
        self.current_room = self.start_coordinates
        self.add_room(self.start_coordinates, theme=entry_theme)
        self.update_player_pos()

    def add_room(self, coordinates, theme=None):
        if theme:
            room_theme = theme
        else:
            room_themes = []
            theme_weights = []
            for values in self.structure['room_themes'].values():
                room_themes.append(values['id'])
                theme_weights.append(values['weight'])
            room_theme = random.choices(room_themes, theme_weights, k=1)[0]

        room_args = {
            'name': self.structure['room_themes'][room_theme]['name'],
            'description': self.structure['room_themes'][room_theme]['description'],
            'coordinates': coordinates,
            'room_theme': room_theme,
            'room_config': self.structure['room_themes'][room_theme],
            'wall_config': self.structure['build'][self.structure['room_themes'][room_theme]['wall_config']],
            'chest': self.generate_chest(room_theme),
            'npc': self.generate_npc(room_theme),
            'items': self.generate_room_items(self.structure['room_themes'][room_theme]),
            'exits': self.build_exits(coordinates, self.structure['room_themes'][room_theme]),
            #'screen_locations': {
            #    direction: {
            #        screen_location: random.choice(
            #            self.structure['room_themes'][room_theme]['screen_locations'][screen_location] or [[]]
            #        )
            #        for screen_location in self.structure['room_themes'][room_theme]['screen_locations'].keys()
            #    }
            #    for direction in ['north', 'south', 'east', 'west']
            #},
            #'screen_background': random.choice(self.structure['room_themes'][room_theme]['walls']),
            #'floor_background': random.choice(self.structure['room_themes'][room_theme]['floors']),
        }

        # screen_background = random.choice(self.structure['room_themes'][room_theme]['walls'])
        # floor_background = random.choice(self.structure['room_themes'][room_theme]['floors'])

        self.room_positions[coordinates] = Room(**room_args)
        self.get_untrod_open_paths(coordinates)

    def adjacent_coordinates(self, direction, coordinates):
        x, y, z = coordinates 
        return {
            'north': (x, y, z + 1),
            'south': (x, y, z - 1),
            'east': (x + 1, y, z),
            'west': (x - 1, y, z),
            'up': (x, y + 1, z),
            'down': (x, y - 1, z),
        }[direction]

    def build_exits(self, coordinates, room_config):
        new_room_exits = {}
        directions = ['north', 'south', 'east', 'west', 'up', 'down']

        opposite_directions = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
            'up': 'down',
            'down': 'up',
        }

        # Get the exit types for adjacent rooms so they can be matched
        room_exits = {
            direction: adjacent_room.exits.get(opposite_directions[direction])
            for direction in directions
            if (adjacent_room := self.room_positions.get(self.adjacent_coordinates(direction, coordinates)))
        }

        for exit_direction in directions:
            direction_config = 'default'
            if exit_direction in room_config['directions']:
                direction_config = exit_direction
            possible_exits = {
                k: v
                for k, v in self.structure['build'].items()
                if exit_direction in v['directions'] and k in room_config['directions'][direction_config]['builds']
                # maybe move this so new room can be forced into out of bounds area if needed
                and all(
                    [
                        self.map_limits['min'][axis]
                        <= self.adjacent_coordinates(exit_direction, coordinates)[axis]
                        <= self.map_limits['max'][axis]
                        for axis in range(3)
                    ]
                )
            }
            weights = [possible_exit['weight'] for possible_exit in possible_exits.values()]

            if room_exit := room_exits.get(exit_direction):
                if room_exit['id'] == 'upstairs':
                    new_room_exits[exit_direction] = deepcopy(self.structure['build']['downstairs'])
                elif room_exit['id'] == 'downstairs':
                    new_room_exits[exit_direction] = deepcopy(self.structure['build']['upstairs'])
                else:
                    if room_exit['id'] in possible_exits.keys(): 
                        new_room_exits[exit_direction] = room_exit
                    else:
                        new_room_exits[exit_direction] = random.choice(
                            [
                                self.structure['build'][build]
                                for build in room_config['directions']['default']['builds']
                                for config_exit in self.structure['build'][build]
                                if self.structure['build'][build]['sub_type'] == room_exit['sub_type']
                            ]
                        )
                        #new_room_exits[exit_direction]['screen_image'] = room_exit['screen_image']
            elif self.open_paths <= 2 and possible_exits:
                open_possible_exits = {k: v for k, v in possible_exits.items() if not v['solid']}
                new_room_exits[exit_direction] = deepcopy(
                    self.structure['build'][random.choice(list(open_possible_exits.keys()))]
                )
            elif possible_exits:
                new_room_exits[exit_direction] = deepcopy(
                    self.structure['build'][random.choices(list(possible_exits.keys()), weights=weights)[0]]
                )
            elif exit_direction in ['up', 'down']:
                new_room_exits[exit_direction] = deepcopy(self.structure['build']['floor'])
            else:
                new_room_exits[exit_direction] = deepcopy(self.structure['build']['wall'])

            """
            new_room_exits[exit_direction]['screen_image'] = random.choice(
                new_room_exits[exit_direction].get('screen_image') or [[]]
            )
            new_room_exits[exit_direction]['blocking_image'] = random.choice(
                new_room_exits[exit_direction].get('blocking_image') or [[]]
            )
            """
            if not new_room_exits[exit_direction].get('screen_image'): 
                new_room_exits[exit_direction]['screen_image'] = random.choice(
                    new_room_exits[exit_direction].get('screen_image_options') or [None] 
                )
            if not new_room_exits[exit_direction].get('blocking_image'):
                new_room_exits[exit_direction]['blocking_image'] = random.choice(
                    new_room_exits[exit_direction].get('blocking_image_options') or [None]
                )
            if new_room_exits[exit_direction]['screen_image']:
                new_room_exits[exit_direction]['animation_frames'] = self.animations.get(new_room_exits[exit_direction]['screen_image'][0])
            else:
                new_room_exits[exit_direction]['animation_frames'] = None

        return new_room_exits

    def generate_chest(self, room_theme):
        chest_weights = [
            1,
            *[
                chest_type['weight']
                for chest_type in self.structure['chests'].values()
                if chest_type['id'] in self.structure['room_themes'][room_theme]['chests']
            ],
        ]
        if len(chest_weights) > 1 and (
            chest_type := random.choices([None, *list(self.structure['chests'].keys())], weights=chest_weights, k=1)[0]
        ):
            return Chest(chest_type, self.structure, self.items_config)

    def generate_npc(self, room_theme):
        if npc_config := self.structure['room_themes'][room_theme]['npcs']:
            npcs = []
            npc_weights = []
            for npc_type in npc_config:
                npcs.append(npc_type)
                npc_weights.append(self.structure['npcs'][npc_type]['weight'])
            # weights = [1, *npc_weights]
            # if npc_type := random.choices([None, *npcs], weights=weights, k=1)[0]:
            if npc_type := random.choices(npcs, weights=npc_weights, k=1)[0]:
                return self.structure['npcs'][npc_type]

    def generate_room_items(self, room_config):
        room_items = BaseContainer(10, room_config['name'])

        for item_type in room_config['item_types']:
            weights = [item['weight'] for item in self.items_config[item_type].values()]
            num_items = random.choice([0, 0, 0, 0, 1])
            items = list(self.items_config[item_type].keys())
            for item in set(random.choices(items, weights=weights, k=num_items)):
                room_items.add_item(deepcopy(self.items_config[item_type][item]))
        return room_items

    def get_current_room(self):
        return self.room_positions[self.current_room]

    def exit_room(self, direction):
        path = self.get_current_room().exits[direction]
        if path['solid'] and path['pass_with']:
            return "You must use a {} to pass through a {}".format(' or '.join(path['pass_with']), path['name'])
        elif path['solid']:
            return f"You can not pass through a {path['name']}"

        new_coordinates = self.adjacent_coordinates(direction, self.current_room)

        if new_coordinates not in self.room_positions.keys():
            self.add_room(new_coordinates)
        if direction not in ['up', 'down'] and self.get_current_room().screen_views[direction].animation:
            self.get_current_room().screen_views[direction].animation.play_animation()
        old_coords = self.current_room
        self.current_room = new_coordinates
        self.update_player_pos(direction=direction, past_room=old_coords)

    def get_untrod_open_paths(self, room_coordinates):
        amount = {True: -1, False: 1}

        room = self.room_positions[room_coordinates]
        self.open_paths += sum(
            [
                amount[bool(self.room_positions.get(self.adjacent_coordinates(direction, room_coordinates)))]
                for direction, room_exit in room.get_exits().items()
                if not room_exit['solid']
                # and not self.room_positions.get(self.adjacent_coordinates(direction))
            ]
        )

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

    def get_map(self, level=None):

        blank_map_image = ['\u2591' * 9] * 7

        m = sorted(self.room_positions.keys(), key=lambda k: [k[1], k[0], k[2]])
        x_coords = [x for x, y, z in m]
        y_coords = [y for x, y, z in m]
        z_coords = [z for x, y, z in m]

        if level is None:
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
