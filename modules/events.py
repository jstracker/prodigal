import os


class ContainerInteraction:
    def __init__(self, containerA, containerB):
        self.containers = {
            'containerA': containerA,
            'containerB': containerB,
        }
        self.current_container = None
        self._starting_selection()

    def _starting_selection(self):
        if self.containers['containerB'].is_empty():
            self.containers['containerA'].change_selected_item(direction=None)
            self.current_container = 'containerA'
        else:
            self.containers['containerB'].change_selected_item(direction=None)
            self.current_container = 'containerB'

    def draw_containers(self):
        print(f"\n{'=' * 10}{self.containers['containerA'].name.title()}{'=' * 10}")
        self.containers['containerA'].view_items()
        print(f"\n{'=' * 10}{self.containers['containerB'].name.title()}{'=' * 10}")
        self.containers['containerB'].view_items()
        self.containers.get(self.current_container, 'containerA').get_interface_options()
        options = ' '.join([f"{letter}- {command}" for letter, command in self.get_interface_options().items()])
        print(f"Available Actions: {options}")
        # get options and print

    def get_current_interface(self):
        return self.containers[self.current_container]

    def get_interface_options(self):
        return self.containers[self.current_container].get_interface_options()

    def interface(self, command):
        container_opposites = {'containerA': 'containerB', 'containerB': 'containerA'}

        if command == 'tab':
            self.containers[self.current_container].remove_selection_box()
            self.current_container = container_opposites[self.current_container]
            self.containers[self.current_container].change_selected_item(direction=None)

        elif command == 'r':
            # RM from current and place in other
            removed_item = self.containers[self.current_container].remove_selected_item()
            self.containers[container_opposites[self.current_container]].add_item(removed_item)

        elif command == 'l':
            selected_item = self.containers[self.current_container].get_selected_item()
            os.system('clear')
            pprint(selected_item)
            input()
        else:    
            self.containers[self.current_container].interface(command)
        self.draw_containers()


class InventoryInteraction(ContainerInteraction):
    def __init__(self, inventory):
        self.containers = {
            'containerA': inventory,
            'containerB': None,
        }
        self.current_container = None

    def load_interaction_container(self, container):
        self.containers['containerB'] = container
        self._starting_selection()
