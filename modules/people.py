from .inventory import Inventory
from .events import InventoryInteraction
from time import sleep


class Player:
    def __init__(self, name):
        self.name = name
        self.max_health = 100
        self.health = 75
        self.max_magic = 20
        self.magic = 10
        self.compass = 'north'
        self.inventory = Inventory()
        self.inventory_interaction = InventoryInteraction(self.inventory)
        self.equipped = {'shield': {}, 'weapon': {}, 'armor': {}}
        self.attack = 1
        self.defense = 1
        self.strength = 1

    def load_structure(self, structure):
        self.structure = structure

    def get_status_bar(self):
        num_keys = self.inventory.keys['num'] 
        hearts = int(self.health / 10) + int(self.health % 10 > 0)
        empty_hearts = int(self.max_health / 10) - hearts
        magic = int(self.magic / 10) + int(self.magic % 10 > 0)
        empty_magic = int(self.max_magic / 10) - magic
        heart_image = ("\u2665" * hearts) + ("\u25CB" * empty_hearts)
        magic_image = ("\uA500" * magic) + ("\u25CB" * empty_magic)
        stats = f"Keys: {num_keys}\n{str(self.health)}/{str(self.max_health)} {heart_image}\n{str(self.magic)}/{str(self.max_magic)} {magic_image}"
        return f"{self.name.title()}\nCompass: {self.compass}\n{stats}"

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
        #while direction not in current_room.exits.keys():
        #    direction = input('move: ').strip()
        #    if direction == 'exit':
        #        return
        tool = None
        if current_room.exits[direction]['solid']:
            if current_room.exits[direction]['id'] == 'locked_door' and self.inventory.keys.get('num'):
                tool = self.inventory.remove_key()
            else:
                print(f"The way is blocked by a {current_room.exits[direction]['name']}")
            current_room.open_room_passage(direction, tool=tool)
        structure.exit_room(direction)

    def add_to_inventory(self, item):
        self.inventory.add_item(item)

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

    def view_inventory(self):
        self.inventory.view_items()

    def inventory_interface(self, command):
        if command == 'u':
            if (item := self.inventory.get_selected_item()) and item.get('use'):
                setattr(self, item['use'], getattr(self, item['use'], 0) + item[item['use']])
                self.inventory.remove_selected_item()
        elif command == 'e':
            pass
        elif command == 'r':
            self.inventory.remove_selected_item()
        else:
            self.inventory.interface(command)

    def equip(self, equipment):
        pass

    def get_inventory_interaction_interface(self, container=None):
        if container:
            self.inventory_interaction.load_interaction_container(container)
        return self.inventory_interaction

    def inventory_interaction_interface(self, command):
        current_interface = self.inventory_interaction.get_current_interface()
        options = current_interface.get_interface_options()
        new_command = options.get(command, command).lower()
        if new_command == 'use':
            current_interface = self.inventory_interaction.get_current_interface()
            if (item := current_interface.get_selected_item()) and item.get('use'):
                setattr(self, item['use'], getattr(self, item['use'], 0) + item[item['use']])
                current_interface.remove_selected_item()
        elif new_command == 'equip':
            pass
        elif new_command == 'remove':
            self.inventory_interaction.interface(command)
        elif new_command == 'unlock':
            current_room = self.structure.get_current_room()
            if current_interface.get_secret_type() == 'key':
                key = self.inventory.remove_key()
                current_interface.unlock(key)
                current_room.create_map_image()
                self.structure.update_player_pos()
        else:
            self.inventory_interaction.interface(new_command)
