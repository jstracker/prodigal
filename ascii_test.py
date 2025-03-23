#! env/bin/python3

import os
import yaml
import modules.new_room as room

from time import sleep
import animations.treasure_chests as chest
import animations.walls as walls
import animations.actions as actions
import modules.animation as animation
#from modules.animation import Animation, animation.get_images
from modules.chests import Chest
from pprint import pprint
import random
#from animations.treasure_chests import closed_chest, opening_chest, half_open_chest, open_chest

"""
with open('images/all_images2.yml', 'r') as infile:
    all_images = yaml.safe_load(infile)
"""

with open('structures/castle.yml', 'r') as infile:
    structure = yaml.safe_load(infile)

with open('rooms/items.yml') as yconfig:
    items_config = yaml.safe_load(yconfig)


"""
def animation.get_images(name, image_type=None, size=None, view=None):
    if image_type == 'backgrounds':
        images = [all_images['backgrounds'][name][size]]
    elif image_type == 'floors':
        images = [all_images['floors'][name][size][view]]
    elif image_type in ['doors', 'chests', 'stairs']:
        images = [all_images[image_type][name][view]]
    else:
        images = [all_images[name]['file']]

    image_list = []
    for image in images:
        with open(image, 'r') as infile:
            image_list.append(infile.read())
    return image_list
"""

blank_screen = animation.get_images('blank_screen', image_type='backgrounds', size='full')
background = animation.get_images('brick_large', image_type='backgrounds', size='full')[0]
floor = [animation.get_images('brick_large', image_type='floors', size='full', view='horizontal_view')[0], [0,0]]

door = random.choice(structure['build']['blocked_door']['screen_image'])
door_block = random.choice(structure['build']['blocked_door']['blocking_image'])
upstairs = random.choice(structure['build']['upstairs']['screen_image'])
downstairs = random.choice(structure['build']['downstairs']['screen_image'])

door_image = [animation.get_images(door[0], image_type='doors', view='closed')[0], door[1]]
door_block_image = [animation.get_images(door_block[0])[0], door_block[1]]
upstairs_image = [animation.get_images(upstairs[0], image_type='stairs', view='up')[0], upstairs[1]]
downstairs_image = [animation.get_images(downstairs[0], image_type='stairs', view='down')[0], downstairs[1]]

images = [floor, door_image, door_block_image, downstairs_image, upstairs_image]
animate = animation.Animation([])
#print(animation.combine_images2(background, images))

#chest = Chest('key_chest', structure, items_config)
#door = structure['build']['blocked_door']
chest = [animation.get_images('treasure_chest', image_type='chests', view='closed')[0], [30, 0], 0]
stairs = {}
door_type = random.choice(list(structure['build'].keys()))
door = structure['build'][door_type]
while door['id'] in ['upstairs', 'downstairs']:
    if door['id'] not in list(stairs.keys()):    
        stairs[door['id']] = (random.choice(door['screen_image']))
    door_type = random.choice(list(structure['build'].keys()))
    door = structure['build'][door_type]
door_image = random.choice(door['screen_image']) if door['screen_image'] else None
door_block = random.choice(door['blocking_image']) if door['blocking_image'] else None 
wall = room.WallImage(structure, 'north', 'brick_large', 'brick_large', door=door_image, door_block=door_block, stairs=stairs, chest=chest)
wall2 = room.WallImage(structure, 'north', 'brick_large', 'brick_large', door=door_image, door_block=door_block, stairs=None, chest=None)
wall.print_wall()
sleep(2)

animate.turn_frames(wall.get_screen_image(), wall2.get_screen_image())
#animate.wipe_frames(wall.get_screen_image(), wall2.get_screen_image())
#wall2.print_wall()
#wall.change_screen('bottom_center', [[animation.get_images(door_image[0], image_type='doors', view='closed')[0], door_image[1], door_image[2]]])
#wall.build_screen()
#wall.print_wall()


""" Wall 
with open('animations/images/brick_wall_full.img', 'r') as wall:
    background = wall.read()

#with open('animations/images/stairs_spiral_down_full.img', 'r') as stairs:
#with open('animations/images/stairs_spiral_up_full.bak', 'r') as stairs:
with open('animations/images/stairs_spiral_up_full.img', 'r') as stairs:
    stairs_up = stairs.read()

with open('animations/images/closed_chest.img', 'r') as chest:
    closed_chest = chest.read()

#with open('animations/images/castle_door_full.img', 'r') as door:
with open('animations/images/iron_door_full.img', 'r') as door:
    castle_door = door.read()

animation = Animation([])

#  stairs up = (0, 120)
# door = (10, 60)
# chest = (30,0)
# stairs down = (21, 119)
# witch/wizard = (20, 60)
# baphomet = (10, 85)
# bookshelf_1 = (13, x)
print(animation.combine_images(background, [stairs_up, closed_chest, castle_door], [(0, 120), (30,0), (10, 60)]))
"""
""" stacked boulders
with open('animations/images/brick_wall_full.img', 'r') as wall:
    background = wall.read()

#with open('animations/images/stairs_spiral_down_full.img', 'r') as stairs:
with open('animations/images/stairs_spiral_up_full.img', 'r') as stairs:
    stairs_up = stairs.read()

#with open('animations/images/closed_chest.img', 'r') as chest:
#with open('animations/images/telescope.img', 'r') as chest:
with open('animations/images/baphomet.img', 'r') as obj:
    room_object = obj.read()

#with open('animations/images/castle_door_full.img', 'r') as door:
with open('animations/images/bookshelf_1.img', 'r') as door:
    bookshelf = door.read()

with open('animations/images/boulders_stacked.img', 'r') as door:
    boulder_stack = door.read()
"""
with open('animations/images/iron_door_full.img', 'r') as door:
    castle_door = door.read()

#animation = Animation([])
#print(animation.combine_images(background, [bookshelf], [(13, 50)]))

#  stairs up = (0, 120)
# door = (10, 60)
# chest = (30,0)
# work table = (28, 0)
# boulders = (30, 90), (30, 70), (30, 60), (20, 80), (20, 65), (10, 70)
#print(animation.combine_images(background, [stairs_up, closed_chest, hole_door, boulder, boulder, boulder, boulder, boulder, boulder], [(21, 119), (30,0), (10, 60), (30, 90), (30, 70), (30, 60), (20, 80), (20, 65), (10, 70)]))
#print(animation.combine_images(background, [hole_door, boulder_stack,], [(10, 60), (10, 60)]))
#with open('animations/unlock_chest.yml', 'r') as infile:
#    unlock_chest_animation = yaml.safe_load(infile)
#



""" witch and bat
with open('animations/images/brick_wall_full.img', 'r') as wall:
    background = wall.read()

with open('animations/images/witch_full.img', 'r') as w:
    witch = w.read()

with open('animations/images/bat.img', 'r') as b:
    bat = b.read()

animation = Animation([])

print(animation.combine_images(background, [witch, bat], [(20, 60), (20, 100)]))
"""

"""
frames = []
for image in unlock_chest_animation['frames']:
    with open(f'animations/images/{image}.img', 'r') as i:
        frames.append(i.read())
animation = Animation(frames, frame_times=unlock_chest_animation['frame_times'])
animation.build_scene(background, unlock_chest_animation['positions'])
animation.play_animation()
"""

"""
for image in frames:
    print(image)
    sleep(1)
"""
#print(background.splitlines())
#for line in background.splitlines():
#    print(line)
#exit()
"""
frames = [chest.closed_chest, chest.opening_chest, chest.half_open_chest, chest.open_chest]
frames = ["closed_chest", "opening_chest", "half_open_chest", "open_chest"]
frame_times = [1, .05, .25, 1]
positions = [(2,4), (2, 4), (2, 4), (2, 4)]
"""
#background = walls.brick
"""
#frames = [background, actions.tiny_explosion, actions.small_explosion, actions.small_explosion, actions.small_explosion, actions.small_explosion, actions.small_explosion, actions.big_explosion]
ck_chest_animation
frames = ["background", "actions.tiny_explosion", "actions.small_explosion", "actions.small_explosion", "actions.small_explosion", "actions.small_explosion", "actions.small_explosion", "actions.big_explosion"]
positions = [(0,0), (20, 30), (20, 25), (70, 40), (40, 80), (30, 40), (15, 80), (15, 40)]
frame_times = [.2, .2, .2, .2, .2, .2, .2, .2]
"""
#x = {'frames': frames, 'positions': positions, 'frame_times': frame_times}
#with open('animations/animations.yml', 'a') as outfile:
#    yaml.dump({'unlock_chest': x}, outfile, default_flow_style=True)



"""
animation = Animation(frames, frame_times=frame_times)
animation.build_scene(background, positions)
animation.play_animation()
"""
