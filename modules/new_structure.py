import random
#from .room import Room
from modules.new_room import Room


class Structure:
    def __init__(self, structure_config, items_config, start_coordinates=None, map_limits=None, entry_theme='default'):
        self.structure = structure_config
        self.items_config = items_config
        self.open_paths = 0
        self.map_limits = map_limits or {'max': (3, 4, 3), 'min': (-1, -4, -4)}
        self.start_coordinates = start_coordinates or (0, 0, self.map_limits['min'][2] - 1) 
        self.room_positions = {}
        self.add_room(self.start_coordinates, theme=entry_theme)
        self.current_room = self.start_coordinates
        self.update_player_pos()

    def add_room(self, coordinates, theme=None):
        x, y, z = coordinates
        if theme:
            room_theme = theme
        else:
            room_themes = []
            theme_weights = []
            for values in self.structure['room_themes'].values():
                room_themes.append(values['id'])
                theme_weights.append(values['weight'])
            room_theme = random.choices(room_themes, theme_weights, k=1)[0]

        self.room_positions[coordinates] = Room(self.structure, self.items_config, self.map_limits, coordinates, self.room_positions, self.open_paths, room_theme=room_theme)
        self.get_untrod_open_paths(coordinates)

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
            return "You must use a {} to pass through a {}".format(' or '.join(path['pass_with']), path['name'])
        elif path['solid']:
            return f"You can not pass through a {path['name']}"

        new_coordinates = direction_coords[direction]

        if new_coordinates not in self.room_positions.keys():
            self.add_room(new_coordinates)
        old_coords = self.current_room
        self.current_room = new_coordinates
        self.update_player_pos(direction=direction, past_room=old_coords)

    def get_untrod_open_paths(self, room_coordinates):
        amount = {True: -1, False: 1}

        room = self.room_positions[room_coordinates]
        self.open_paths += sum(
            [
                amount[bool(self.room_positions.get(room.adjacent_positions[direction]))]
                for direction, room_exit in room.get_exits().items()
                if not room_exit['solid']
                #and not self.room_positions.get(self.adjacent_positions[direction])
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
