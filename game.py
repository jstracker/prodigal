#! env/bin/python

#import curses
import os
import readline
import yaml

from pprint import pprint
from rooms import room
from sshkeyboard import listen_keyboard, stop_listening
from time import sleep



"""
screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
#curses.resizeterm(10, 10)
#curses.napms(3000)
screen.refresh()
"""


def press(key):
        stop_listening()
        global inside_structure
        global view
        if key == 'up':
            player.move(structure, direction='north')
        elif key  == 'down':
            player.move(structure, direction='south')
        elif key == 'right':
            player.move(structure, direction='east')
        elif key == 'left':
            player.move(structure, direction='west')
        elif key == 'pageup':
            player.move(structure, direction='up')
        elif key == 'pagedown':
            player.move(structure, direction='down')
        elif key == 'm':
            structure.get_map()
            input("Press enter exit")
        elif key == 'v':
            view = {'room': 'map', 'map': 'room'}[view]
        elif key == 'p':
            os.system('reset')
            player.pickup_item(structure)
        elif key == 'i':
            os.system('reset')
            player.inventory()
        elif key == 'u':
            player.unlock_chest(structure)
        elif key == 'o':
            player.open_chest(structure) 
            input("Press enter exit")
        elif key == 'x':
            inside_structure = False

    
player_name = input("Choose character name: ")
player = room.Player(player_name)
structure = room.Structure()
player.load_structure(structure)
inside_structure = True
view = 'room'
    

def main():
    #game_type = ''
    #while game_type.lower() not in ['new', 'n', 'load', 'l']:
    #    game_type = input("Load game or new game?: ").strip()
    
    #if game_type == 'new':
    #    structure = room.Structure()
    #else:
    #    with open('save.yml', 'r') as save_file:
    #        structure = yaml.load(save_file)
    
    
    actions = ['exit', 'save', 'map', 'move', 'search', 'pickup', 'inventory', 'view']
    #inventory = room.Inventory()
    #inventory.open_inventory()
    while inside_structure:
        actions = ['exit', 'save', 'map', 'move', 'search', 'pickup', 'inventory', 'view']
        current_room = structure.get_current_room()
        if current_room.chest and current_room.chest.locked:
            actions.append('unlock chest')
        elif current_room.chest and not current_room.chest.locked:
            actions.append('open chest')
        os.system('clear')
        if view == 'room':
            print('\n'.join(current_room.map_image))
        elif view == 'map':
            structure.get_map(level=current_room.coordinates[1])
        print(current_room)
        print(f"\nkeys: {player.items.get('key', {'num': 0})['num']}\t\tMoney: {player.money}")
        print(f"\nVisible items in room: {list(current_room.items.keys())}")
        print(f"Available Actions: {actions}")
        listen_keyboard(on_press=press, sequential=True)

        """ 
        if action == 'save':
            with open('save.yml', 'w') as save_file:
               yaml.safe_dump(structure, save_file)
    
        if action == 'look':
            pass
    
        if action == 'pickup':
            player.pickup_item(current_room)
        """
    
    
    
if __name__ == '__main__':
    try:
        main()
    finally:
        """
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()
        """
