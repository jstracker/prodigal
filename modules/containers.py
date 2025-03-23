import uuid

from copy import deepcopy


class BaseContainer:
    def __init__(self, num_slots, name='', stack_items=False, locked=False):
        self.name = name
        self.max_per_row = 10
        self.max_column_view = 10
        self.num_slots = num_slots
        self.items = {}
        self.item_ids = []
        self.order_by = 'type'
        self.stack_items = stack_items
        self.current_selection = None
        self.locked = False 

    def interface(self, command):

        commands = {
            'pageup': lambda direction: None,
            'pagedown': lambda direction: None,
            'up': self.change_selected_item,
            'down': self.change_selected_item,
            'left': self.change_selected_item,
            'right': self.change_selected_item,
        }

        commands.get(command, lambda direction: None)(direction=command)

    def get_interface_options(self):
        return {'u': 'Use', 'r': 'Remove', 'e': 'Equip', 'x': 'eXit'}

    def add_slots(self, num_slots):
        self.num_slots += num_slots

    def generate_item_image(self, item):
        name = item['name']
        item_keys = ['damage', 'durability', 'health', 'num', 'defense', 'perception']
        stats = " ".join([f"{item_key}={item[item_key]}" for item_key in item_keys if item.get(item_key)])

        if self.current_selection == item['container_id']:
            tl_corner, bl_corner, tr_corner, br_corner, side, top_bot = (
                "\u250C",
                "\u2514",
                "\u2510",
                "\u2518",
                "\u2502",
                "\u2500",
            )
        else:
            tl_corner, bl_corner, tr_corner, br_corner, side, top_bot = [""] * 6

        entry = f"{name}: {stats}"
        entry_length = len(entry)
        item['display_image'] = [
            f"{tl_corner}{top_bot * entry_length}{tr_corner}",
            f"{side}{entry}{side}",
            f"{bl_corner}{top_bot * entry_length}{br_corner}",
        ]

    def get_items_by_type(self, item_type, item_id=None):
        if item_id:
            return [item for item in self.items.values() if item['type'] == item_type and item['id'] == item_id]
        return [item for item in self.items.values() if item['type'] == item_type]

    def get_item_list(self):
        return [item['name'] for item in self.items.values()]

    def add_item(self, item):
        if self.stack_items and item.get('max_stack', 1) > 1:
            for values in self.items.values():
                if values['id'] == item['id'] and values.get('num', 1) < values['max_stack']:
                    if (total := item.get('num', 1) + values.get('num', 1)) > values['max_stack']:
                        item['num'] = total - values['max_stack']
                        values['num'] = values['max_stack']
                        self.generate_item_image(self.items[values['container_id']])
                    else:
                        values['num'] = total
                        self.generate_item_image(self.items[values['container_id']])
                        return

        if len(self.items) < self.num_slots:
            container_id = item.setdefault('container_id', str(uuid.uuid4()))
            self.items.setdefault(container_id, item)
            self.item_ids.append(container_id)
            self.generate_item_image(self.items[container_id])
            self.reorder_items()
        else:
            print("There are no empty slots!!")

    def remove_selected_item(self):
        removed_id = self.current_selection
        if self.stack_items and self.items[removed_id].get('max_stack', 1) > 1:
            if self.items[removed_id].get('num', 1) > 1:
                new_item = deepcopy(self.items[removed_id])
                new_item['num'] = 1
                new_item['container_id'] = str(uuid.uuid4())
                self.items[removed_id]['num'] -= 1
                self.generate_item_image(self.items[removed_id])
                return new_item

        if len(self.item_ids) > 1:
            self.change_selected_item(direction='right')
        else:
            self.current_selection = None
        self.item_ids.pop(self.item_ids.index(removed_id))
        return self.items.pop(removed_id)

    def view_items(self):
        for item_id in self.item_ids:
            print("\n".join(self.items[item_id]['display_image']).strip())

    def get_selected_item(self):
        return self.items[self.current_selection]

    def change_selected_item(self, direction):
        if self.is_empty() or self.is_locked():
            return
        old_index = None
        new_index = 0
        if self.current_selection in self.item_ids:
            old_index = self.item_ids.index(self.current_selection)

            if direction:
                directions = {
                    'up': old_index - 1,
                    'down': old_index + 1,
                    'left': old_index - 1,
                    'right': old_index + 1,
                }

                new_index = directions[direction]

                if new_index >= len(self.item_ids):
                    new_index = 0

        self.current_selection = self.item_ids[new_index]

        for item_index in [old_index, new_index]:
            if isinstance(item_index, int):
                self.generate_item_image(self.items[self.item_ids[item_index]])

    def remove_selection_box(self):
        if self.current_selection:
            old_selection = self.current_selection
            self.current_selection = None
            self.generate_item_image(self.items[old_selection])

    def reorder_items(self, reorder_key=None):
        self.order_by = reorder_key or self.order_by
        self.item_ids[:] = sorted(self.item_ids, key=lambda x: self.items[x][self.order_by])

    def is_empty(self):
        return not bool(len(self.items))

    def is_locked(self):
        return self.locked

    def unlock(self):
        self.locked = False
