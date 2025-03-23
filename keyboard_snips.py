import keyboard

"""
def key_menu():
    event = keyboard.read_event(suppress=True)
    print('past event')
    if True: #event.event_type == keyboard.KEY_DOWN:
        if event.name == 'up':
            player.move(structure, direction='north')
        elif event.name == 'down':
            player.move(structure, direction='south')
        elif event.name == 'right':
            player.move(structure, direction='east')
        elif event.name == 'left':
            player.move(structure, direction='west')
        elif event.name == 'page up':
            player.move(structure, direction='up')
        elif event.name == 'page down':
            player.move(structure, direction='down')
        elif event.name == 'm':
            structure.get_map()
            input()
        elif event.name == 'v':
            view = {'room': 'map', 'map': 'room'}[view]
        elif event.name == 'p':
            player.pickup_item(structure)
        elif event.name == 'i':
            player.inventory()
        elif event.name == 'u':
            player.unlock_chest(structure)
        elif event.name == 'o':
            player.open_chest(structure) 
            input()
    return event.name
"""
"""
keyboard.add_hotkey('up', lambda: player.move(structure, direction='north'))
keyboard.add_hotkey('down', lambda: player.move(structure, direction='south'))
keyboard.add_hotkey('right', lambda: player.move(structure, direction='east'))
keyboard.add_hotkey('left', lambda: player.move(structure, direction='west'))
keyboard.add_hotkey('page up', lambda: player.move(structure, direction='up'))
keyboard.add_hotkey('page down', lambda: player.move(structure, direction='down'))
keyboard.add_hotkey('m', lambda: structure.get_map())
#keyboard.add_hotkey('v', )
keyboard.add_hotkey('p', lambda: player.pickup_item(current_room))
keyboard.add_hotkey('i', lambda: player.inventory())
keyboard.add_hotkey('u', lambda: player.unlock_chest(structure))
keyboard.add_hotkey('o', lambda: player.open_chest(structure))
"""
"""
keyboard.add_hotkey('up', player.move, args=(structure, 'north'))
keyboard.add_hotkey('down', player.move, args=(structure, 'south'))
keyboard.add_hotkey('right', player.move, args=(structure, 'east'))
keyboard.add_hotkey('left', player.move, args=(structure, 'west'))
keyboard.add_hotkey('page up', player.move, args=(structure, 'up'))
keyboard.add_hotkey('page down', player.move, args=(structure, 'down'))
keyboard.add_hotkey('m', structure.get_map)
#keyboard.add_hotkey('v', )
keyboard.add_hotkey('p', player.pickup_item, args=(structure))
keyboard.add_hotkey('i', player.inventory)
keyboard.add_hotkey('u', player.unlock_chest, args=(structure))
keyboard.add_hotkey('o', player.open_chest, args=(structure))
"""
keyboard.read_hotkey(suppress=True)
