import uuid
from .containers import BaseContainer
from copy import deepcopy


class Inventory:
    def __init__(self, name='Inventory'):
        self.name = name
        self.money = 0
        self.keys = {'num': 0}
        self.items = BaseContainer(10, stack_items=True)
        self.food = BaseContainer(10, stack_items=True)
        self.tools = BaseContainer(10, stack_items=True)
        self.weapons = BaseContainer(10, stack_items=True)
        self.armor = BaseContainer(10, stack_items=True)
        self.types_map = {
            'items': self.items,
            'food': self.food,
            'tools': self.tools,
            'weapons': self.weapons,
            'armor': self.armor,
        }

        self.current_container = 'items'

    def interface(self, command, item=None):

        commands = {
            'pageup': self.change_selected_container,
            'pagedown': self.change_selected_container,
            'up': self.change_selected_item,
            'down': self.change_selected_item,
            'left': self.change_selected_item,
            'right': self.change_selected_item,
        }

        commands.get(command, lambda command: None)(command)

    def get_interface_options(self):
        return {'u': 'Use', 'r': 'Remove', 'e': 'Equip', 'x': 'eXit'}

    def get_items_by_type(self, item_type, item_id=None):
        if item_type in self.types_map.keys():
            items = self.types_map.get(item_type)
            return items.get_items_by_type(item_type, item_id=item_id)
        return []

    def view_items(self):
        print(f"Money: ${self.money}\n")
        for item_type, container in self.types_map.items():
            print(f"{item_type.title()}:")
            container.view_items()
            print("\n\n")

    def change_selected_container(self, direction):
        container_options = list(self.types_map.keys())
        current_index = container_options.index(self.current_container)

        directions = {
            'pageup': current_index - 1,
            'pagedown': current_index + 1,
        }

        new_index = directions[direction]
        if direction in ['pageup', 'pagedown']:
            self.types_map[self.current_container].remove_selection_box()

        if new_index >= len(container_options):
            new_index = 0

        self.current_container = container_options[new_index]
        self.types_map[self.current_container].change_selected_item(direction=None)

    def change_selected_item(self, direction):
        self.types_map[self.current_container].change_selected_item(direction=direction)

    def get_selected_item(self):
        return self.types_map[self.current_container].get_selected_item()

    def remove_selection_box(self):
        self.types_map[self.current_container].remove_selection_box()

    def add_slots(self, num_slots, item_type):
        self.types_map[self.current_container].add_slots()

    def add_money(self, item):
        self.money += item['amount']

    def subtract_money(self, amount):
        self.money -= amount

    def add_keys(self, key_object):
        if self.keys.get('id'):
            self.keys['num'] += key_object.get('num', 1)
        else:
            self.keys.update(key_object)

    def remove_key(self):
        if self.keys.get('num', 0):
            removed_key = deepcopy(self.keys)
            self.keys['num'] -= 1
            removed_key.update({'num': 1, 'container_id': str(uuid.uuid4())})
            return removed_key

    def add_item(self, item):
        item_type = item['type']
        if item_type == 'money':
            self.add_money(item)
        elif item['id'] == 'key_1':
            self.add_keys(item)
        else:
            self.types_map.get(item_type, self.items).add_item(item)

    def remove_selected_item(self):
        return self.types_map[self.current_container].remove_selected_item()
