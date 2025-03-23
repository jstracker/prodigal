from .room import Room


class Structure:
    def __init__(self, structure_config, items_config, start_coordinates=None, max_size=(3, 3, 3)):
        self.structure = structure_config
        self.items_config = items_config
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
        self.room_positions[coordinates] = Room(self.structure, self.items_config, coordinates, self.room_positions, self.open_paths)
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
