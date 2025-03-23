#! env/bin/python3

import os
import random
import readline
import yaml

from copy import deepcopy
from sshkeyboard import listen_keyboard, stop_listening
from time import sleep
from pprint import pprint

from modules.chests import Chest
from modules.containers import BaseContainer
from modules.inventory import Inventory
from modules.events import ContainerInteraction
from modules.people import Player
#from structures import structure
#from modules.new_structure import Structure
from modules.structure_dc import Structure



with open('rooms/items.yml') as yconfig:
    items_config = yaml.safe_load(yconfig)

"""
with open('rooms/structures.yml') as yconfig:
    structure_config = yaml.safe_load(yconfig)
"""

with open('animations/animations.yml') as a_config:
    animation_config = yaml.safe_load(a_config)

with open('structures/castle.yml', 'r') as infile:
    structure_config = yaml.safe_load(infile)


def main_menu(key):
    stop_listening()
    global inside_structure
    global view
    global menu
    directions = {'up': 'north', 'down': 'south', 'right': 'east', 'left': 'west', 'pageup': 'up', 'pagedown': 'down'}

    if view == 'room' and key in ['left', 'right', 'down']:
        room_view(key)
    elif key in (directions.keys()):
        if view == 'room' and key == 'up':
            direction = player.compass
        else:
            direction = directions[key]
            if direction not in ['up', 'down']:
                player.compass = direction
        player.move(structure, direction=direction)
    elif key == 'm':
        structure.get_map()
        input("Press enter exit")
    elif key == 'v':
        view = {'room': 'map', 'map': 'room'}[view]
    elif key in ['p', 'i', 'o']:
        menu = 'container_interaction__menu'
        current_room = structure.get_current_room()
        if key in ['p', 'i']:
            interface = player.get_inventory_interaction_interface(container=current_room.items)
        elif key in ['o']:
            interface = player.get_inventory_interaction_interface(container=current_room.chest)
        os.system('clear')
        print(player.get_status_bar())
        interface.draw_containers()
    elif key == 's':
        with open('save.yml', 'w') as save_file:
            yaml.dump(structure, save_file)
    elif key == 'u':
        print('unlock')
        #player.unlock_chest(structure)
    elif key == 'c':
        print('open')
        #menu = 'container_interaction_menu'
        #player.open_chest(structure) 
        input("Press enter exit")
    elif key == 'x':
            inside_structure = False


def container_interaction_menu(key):
    stop_listening()
    global menu
    if key in ['tab', 'up', 'down', 'right', 'left', 'pageup', 'pagedown', 'u', 'r', 'e', 'l', 'o']:
        interface = player.get_inventory_interaction_interface()
        #interface.interface(key)
        player.inventory_interaction_interface(key)
        os.system('clear')
        print(player.get_status_bar())
        interface.draw_containers()
    elif key == 'x':
        menu = 'main_menu'


def room_view(key):
    stop_listening()
    directions = ['north', 'east', 'south', 'west']
    current_index = directions.index(player.compass)
    if key == 'left':
        player.compass = directions[current_index - 1]
    if key == 'right':
        player.compass = directions[current_index - 3]
    if key == 'down':
        player.compass = directions[current_index - 2]
       

def add_items():
    item_list = []
    for item_type in ['keys', 'items', 'food', 'tools', 'weapons', 'armor', 'money', ]:
        #num_items = random.choice([1, 1, 2, 2, 3])
        num_items = 5
        items = list(items_config[item_type].keys())
        item_list.extend([deepcopy(items_config[item_type][item]) for item in random.choices(items, k=num_items)])

    return item_list


def main_screen():
        actions = ['exit', 'save', 'map', 'look', 'pickup', 'inventory', 'view']
        current_room = structure.get_current_room()
        if current_room.chest:
            actions.append('open chest')
        os.system('clear')
        if view == 'room':
            #print('\n'.join(current_room.map_image))
            #print(current_room.screen_views[player.compass])
            current_room.screen_views[player.compass].print_wall()
        elif view == 'map':
            structure.get_map(level=current_room.coordinates[1])
        print(f"{structure.open_paths=}")
        print(current_room, end='\n')
        print(player.get_status_bar())
        print(f"\nVisible items in room: {current_room.get_item_list()}")
        print(f"Available Actions: {actions}")



item_list = add_items()
player = Player(input("Choose character name: "))
structure_type = 'castle'
#structure = structure.Structure(structure_config[structure_type], items_config)
structure = Structure(structure_config, items_config, animation_config, entry_theme='entrance')

player.load_structure(structure)
inside_structure = True
view = 'room'
menu = 'main_menu'
current_event = None

#chest = Chest('key_chest', structure_config['castle'], items_config)
for item in item_list:
    player.add_to_inventory(item)

menu_options = {
    'main_menu': main_menu,
    'container_interaction__menu': container_interaction_menu,
}

def main():

    while inside_structure:
        if menu == 'main_menu':
            main_screen()
        listen_keyboard(on_press=menu_options[menu], sequential=True)


if __name__ == '__main__':
    main()
