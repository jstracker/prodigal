import random
from collections import defaultdict
from dataclasses import InitVar, dataclass, field
import modules.animation as animation

# Walls get build first and then are passed to room.. chest/npc/etc will be part of a wall?
# if items get visually placed around room, how to handle? Does each wall get a container? lean towards no

# left off on new_room.build_room
@dataclass
class Room:
    #room_args: InitVar[dict] = None
    items: dataclass
    chest: 'typing.Any'
    npc: 'typing.Any'
    name: str = field(default_factory=str)
    description: str = field(default_factory=str)
    room_theme: str = field(default_factory=str)
    #structure_config: InitVar[dict | None] = None
    #items_config: InitVar[dict | None] = None
    # walls: 'typing.Any'
    room_config: dict = field(default_factory=dict)
    wall_config: dict = field(default_factory=dict)
    screen_locations: dict = field(default_factory=dict)
    screen_background: list = field(default_factory=list)
    floor_background: list = field(default_factory=list)
    coordinates: tuple = field(default_factory=tuple)
    exits: dict = field(default_factory=dict)
    map_image: list = field(default_factory=list, init=False)
    screen_views: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        directions = ['north', 'south', 'east', 'west']
        screen_parts = [
            'top_left',
            'top_center',
            'top_right',
            'bottom_left',
            'bottom_center',
            'bottom_right',
            'foreground',
        ]
        self.screen_locations = defaultdict(dict)
        for direction in directions:
            self.screen_locations[direction]['background'] = random.choice(
                self.room_config['directions'].get(
                    direction, self.room_config['directions']['default']
                )['walls']
            )
            self.screen_locations[direction]['floor'] = random.choice(
                self.room_config['directions'].get(
                    direction, self.room_config['directions']['default']
                )['floors']
            )

            direction_config = 'default'
            if direction in self.room_config['directions']:
                direction_config = direction
            for screen_location, image_metas in self.room_config['directions'][direction_config]['screen_locations'].items():
                self.screen_locations[direction][screen_location] = random.choice(image_metas or [[]])
            #'screen_locations': {
            #    direction: {
            #        screen_location: random.choice(
            #            self.structure['room_themes'][room_theme]['screen_locations'][screen_location] or [[]]
            #        )
            #        for screen_location in self.structure['room_themes'][room_theme]['screen_locations'].keys()
            #    }
            #    for direction in ['north', 'south', 'east', 'west']
            #},
        #self.screen_background = random.choice(self.room_config['directions']['default']['walls'])
        #self.floor_background = random.choice(self.room_config['directions']['default']['floors'])

        self.create_map_image()
        self.create_screen_image()

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
            if open_map_image := self.exits[direction].get('open_map_image'):
                self.exits[direction]['map_image'] = open_map_image
            self.create_map_image()
            self.create_screen_image()
            print(f"{passage['name']} opened with {tool['name']}")
        elif passage['solid'] and passage['pass_with']:
            return "You must use a {} to pass through a {}".format(' or '.join(passage['pass_with']), passage['name'])
        elif passage['solid']:
            return f"You can not pass through this {passage['name']}"

    def get_item_list(self):
        return self.items.get_item_list()

    def create_map_image(self):

        images = {
            'north_wall': self.wall_config['north']['map_image'],
            'south_wall': self.wall_config['south']['map_image'],
            'east_wall': self.wall_config['east']['map_image'],
            'west_wall': self.wall_config['west']['map_image'],
            'chest': self.chest.map_image if self.chest else ' ',
            'room_id': self.room_config['map_image'] or ' '
        }

        exit_image = {}
        for direction, room_exit in self.exits.items():
            """
            if room_exit['id'] == 'wall':
                exit_image[direction] = room_exit[direction]['map_image']
            elif room_exit['id'] == 'secret_door':
                exit_image[direction] = images[f"{direction}_wall"]
            else:
                exit_image[direction] = room_exit['map_image']
            """
            exit_image[direction] = room_exit.get('map_image') or images[f"{direction}_wall"]

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
            'upstairs': self.exits['up']['screen_image'],
            'downstairs': self.exits['down']['screen_image']
        }
        chest = None
        npc = None
        if self.chest:
            chest = [animation.get_images(self.chest.screen_image, image_type='chests', view='closed')[0], [30, 0], 0]
        if self.npc:
            npc = [animation.get_images(self.npc['screen_image'][0])[0], self.npc['screen_image'][1], self.npc['screen_image'][2]]
        for exit_dir in ['north', 'south', 'east', 'west']:
            door = self.exits[exit_dir]
            self.screen_views[exit_dir] = WallImage(
                #self.room_config['directions']['default']['screen_locations'],
                compass_location=exit_dir,
                background=self.screen_locations[exit_dir]['background'],
                floor=self.screen_locations[exit_dir]['floor'],
                stairs=stairs,
                npc=npc,
                chest=chest,
                door=door['screen_image'],
                door_block=door['blocking_image'],
                screen_locations=self.screen_locations[exit_dir],
                animation_frames=door['animation_frames']
            )
            stairs.clear()
            chest = None
            npc = None

        def get_screen_views(self):
            return self.screen_views


@dataclass
class WallImage:
    compass_location: str
    background: str
    floor: str
    stairs: dict
    npc: 'typing.Any'
    chest: 'typing.Any' 
    door: list 
    door_block: str
    screen_locations: dict
    animation_frames: dict

    top_left: list = field(default_factory=list)
    top_center: list = field(default_factory=list)
    top_right: list = field(default_factory=list)
    bottom_left: list = field(default_factory=list)
    bottom_center: list = field(default_factory=list)
    bottom_right: list = field(default_factory=list)
    foreground: list = field(default_factory=list)

    screen_image: str = field(init=False)
    animation: str = field(init=False)

    def __post_init__(self):
        if self.compass_location in ['north', 'south']:
            fl_view = 'horizontal_view'
        else:
            fl_view = 'vertical_view'

        self.floor = animation.get_images(self.floor, image_type='floors', size='full', view=fl_view)[0]
        self.background = animation.get_images(self.background, image_type='backgrounds', size='full')[0]
        self.background = animation.combine_images(self.background, [[self.floor, (0, 0), 0]])

        if self.chest:
            self.bottom_left.append(self.chest)
        if self.npc:
            self.foreground.append(self.npc)

        door_image = []
        if self.door:
            door_image.append([animation.get_images(self.door[0], image_type='doors', view='closed')[0], self.door[1], self.door[2]])
            if self.door_block: 
                door_image.append([animation.get_images(self.door_block[0], image_type='blockers', view='closed')[0], self.door_block[1], self.door_block[2]])
            self.bottom_center = door_image

        for screen_location in self.screen_locations.keys():
            if not getattr(self, screen_location):
                if image := self.screen_locations[screen_location]:
                    image_name, pos, level = image
                    image_list = [[image, pos, level] for image in animation.get_images(image_name)]
                    setattr(self, screen_location, image_list)

        stair_images = {}
        if self.stairs and (upstairs := self.stairs.get('upstairs')):
            self.top_right.append([animation.get_images(upstairs[0], image_type='stairs', view='up')[0], upstairs[1], upstairs[2]])
        if self.stairs and (downstairs := self.stairs.get('downstairs')):
            self.bottom_right.append([animation.get_images(downstairs[0], image_type='stairs', view='down')[0], downstairs[1], downstairs[2]])

        self.screen_image = self.build_screen()

        self.animation = None
        if self.animation_frames:
            frame_images = []
            coords, layer = self.door[1:]
            for frame_key in self.animation_frames['frames']:
                frame_image = [animation.get_images(self.door[0], image_type='doors', view=frame_key)[0], coords, layer]
                frame_images.append(self.build_screen(bottom_center=[frame_image]))
            self.animation = animation.Animation(frame_images, frame_times=self.animation_frames['frame_times'])
            self.animation.build_scene(self.background, [[0, 0]] * len(frame_images))


    def build_screen(self, bottom_center=None):
        if not bottom_center:
            bottom_center = self.bottom_center
        return animation.combine_images(
            self.background, [
                x for x in [
                    *self.top_left,
                    *self.bottom_left,
                    *self.top_right,
                    *self.bottom_right,
                    *self.top_center,
                    *bottom_center, # or *self.bottom_center,
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
