import os
from collections import deque
import re
import yaml

from copy import deepcopy
from time import sleep


with open('images/all_images2.yml', 'r') as infile:
    all_images = yaml.safe_load(infile)

    
class Animation:
    def __init__(self, frames, frame_times=None):
        self.frames = frames
        self.frame_times = frame_times or [1] * len(frames)
        self.animation_frames = []

    def play_animation(self):
        os.system('clear')
        print(self.animation_frames[0])
        for animation, frame_time in zip(self.animation_frames, self.frame_times):
            os.system('clear')
            print(animation)
            sleep(frame_time)

    def role_frames(self, start_image, end_image, direction='right'):
        start = [deque([letter for letter in line]) for line in start_image.splitlines()]
        end = [deque([letter for letter in line]) for line in end_image.splitlines()]
        no_lines = range(len(end))
        no_letters = range(len(end[0]))
        for letter in no_letters:
            if direction == 'left':
                for line in no_lines:
                    start[line].appendleft(end[line].pop())
                    start[line].pop()
            elif direction == 'right':
                for line in no_lines:
                    start[line].append(end[line].popleft())
                    start[line].popleft()
            if letter % 10:
                os.system('clear')
                print('\n'.join([''.join(line) for line in start]))
                sleep(.05)
        
        os.system('clear')
        print('\n'.join([''.join(line) for line in start]))

    def turn_frames(self, start_image, end_image, direction='right'):
        #master = deque([deque([letter for letter in line]) for line in start_image.splitlines()])
        x = start_image.splitlines()
        master = [deque([line[letter] for line in x]) for letter in range(len(x[0]))]

        start = deque([deque([letter for letter in line]) for line in start_image.splitlines()]) 
        end = [deque([letter for letter in line]) for line in end_image.splitlines()]
        num_lines = len(end)
        num_letters = len(end[0])
        for letter in range(num_letters):
            if letter % 3:
                for column in range(len(master) - 1 - letter,  len(master)):
                    master[column][-1] = ''
                    master[column].rotate(1)
                for line in range(num_lines):
                    for l in range(letter, num_letters):
                        start[line][l] = master[l][line]
            """    
            for l in range(letter, num_letters):
                master[0][l] = '.'
            """
            """
            for line in range(num_lines - 1, -1, -1):
                if line == num_lines - 1:
                    for _ in range(letter, num_letters):
                        start[line].pop()
                elif :
                else:
                    for l in range(letter, num_letters - letter):
                        start[line + 1].append(start[line].pop())
            """
            if direction == 'left':
                for line in range(num_lines):
                    start[line].appendleft(end[line].pop())
                    start[line].pop()
            elif direction == 'right':
                for line in range(num_lines):
                    start[line].append(end[line].popleft())
                    start[line].popleft()
            if letter % 10:
                os.system('clear')
                print('\n'.join([''.join(line) for line in start]))
                sleep(.01)
                #sleep(1)
        
        os.system('clear')
        print('\n'.join([''.join(line) for line in start]))

    def wipe_frames(self, start_image, end_image, direction=None):
        start = [[letter for letter in line] for line in start_image.splitlines()]
        end = [[letter for letter in line] for line in end_image.splitlines()]
        no_lines = range(len(end))
        no_letters = range(len(end[0]))
        for letter in no_letters:
            for line in no_lines:
                start[line][letter] = end[line][letter]
            if letter % 10:
               os.system('clear')
               print('\n'.join([''.join(line) for line in start]))
               sleep(.005)    
        os.system('clear')
        print('\n'.join([''.join(line) for line in start]))

    def get_frames(self):
        return self.animation_frames

    def build_scene(self, background, positions):
        #background = [re.split(r'(\s)', line) for line in background.splitlines()]
        #background = [letter for line in background.splitlines() for letter in line]
        background = [[letter for letter in line] for line in background.splitlines()]
        for frame, pos  in zip(self.frames, positions):
            clean_background = deepcopy(background)
            #new_frame = [re.split(r'(\s)', line) for line in frame.splitlines()]
            new_frame = [[letter for letter in line] for line in frame.splitlines()]
            for x in range(len(new_frame)):
                image_start = False
                for y in range(len(new_frame[x])):
                    if not new_frame[x][y].isspace() and not image_start:
                        image_start = True
                    try:
                        if image_start:
                            clean_background[x + pos[0]][y + pos[1]] = new_frame[x][y]
                            #clean_background[x + pos[0]][y + pos[1]] = new_frame[x][y] or background[x][y]
                    except Exception as e:
                        raise e 
                        
            self.animation_frames.append('\n'.join([''.join(line) for line in clean_background]))
        #print(clean_background)

    def combine_images(self, background, images, positions):
        split_images = []

        new_image = [[letter for letter in line] for line in background.splitlines()]
        for image, pos in zip(images, positions):
            split_image = [[letter for letter in line] for line in image.splitlines()]
            for x in range(len(split_image)):
                image_start = False
                for y in range(len(split_image[x])):
                    try:
                        if not split_image[x][y].isspace() and not image_start:
                            image_start = True
                            #new_image[x + pos[0]][y + pos[1]] = split_image[x][y] or new_image[x][y]
                            #new_image[x + pos[0]][y + pos[1]] = split_image[x][y] # or new_image[x + pos[0]][y + pos[1]]
                        if image_start:
                            #new_image[x + pos[0]][y + pos[1]] = new_image[x][y]
                            #new_image[x + pos[0]][y + pos[1]] = new_image[x + pos[0]][y + pos[1]]
                            new_image[x + pos[0]][y + pos[1]] = split_image[x][y]
                    except Exception as e:
                        raise e
        return '\n'.join([''.join(line) for line in new_image])

    def combine_images2(self, background, images):
        split_images = []

        #background_image = [[letter for letter in line] for line in background.splitlines()]

        new_image = [[letter for letter in line] for line in background.splitlines()]
        background_image = deepcopy(new_image)
        #new_image = deepcopy(background_image)
        for image, pos in images:
            transparency = False
            split_image = [[letter for letter in line] for line in image.splitlines()]
            check_letter = split_image[-1][-1]
            if check_letter == 'T':
                transparency = True
                split_image[-1].pop(-1)
            if check_letter == 'K':
                split_image[-1].pop(-1)
                background_image = deepcopy(new_image)
            for x in range(len(split_image)):
                image_start = False
                for y in range(len(split_image[x])):
                    try:
                        if not split_image[x][y].isspace() and not image_start:
                            image_start = True
                            #new_image[x + pos[0]][y + pos[1]] = split_image[x][y] or new_image[x][y]
                            #new_image[x + pos[0]][y + pos[1]] = split_image[x][y] # or new_image[x + pos[0]][y + pos[1]]
                        if image_start and not transparency:
                            #new_image[x + pos[0]][y + pos[1]] = new_image[x][y]
                            #new_image[x + pos[0]][y + pos[1]] = new_image[x + pos[0]][y + pos[1]]
                            new_image[x + pos[0]][y + pos[1]] = split_image[x][y]
                        elif image_start and transparency:
                            if split_image[x][y] == '0':
                                new_image[x + pos[0]][y + pos[1]] = background_image[x + pos[0]][y + pos[1]]
                    except Exception as e:
                        print(pos, x, y)
                        raise e
        return '\n'.join([''.join(line) for line in new_image])


def combine_images(background, images):
    split_images = []
    new_image = [[letter for letter in line] for line in background.splitlines()]
    images.sort(key=lambda x: x[2])
    for image, pos, level in images:
        ignore = ''
        split_image = [[letter for letter in line] for line in image.splitlines()]
        check_letter = split_image[-1][-1]
        if check_letter == 'T':
            split_image[-1].pop(-1)
            ignore = split_image[-1].pop(-1)
        for x in range(len(split_image)):
            image_start = False
            for y in range(len(split_image[x])):
                try:
                    if not split_image[x][y].isspace() and not image_start:
                        image_start = True
                    if image_start and split_image[x][y] != ignore and x + pos[0] < len(new_image) and y + pos[1] < len(new_image[x + pos[0]]):
                        new_image[x + pos[0]][y + pos[1]] = split_image[x][y]
                except Exception as e:
                    print(pos, x, y)
                    raise e
    return '\n'.join([''.join(line) for line in new_image])


def get_images(name, image_type=None, size=None, view=None):
    try:
        if image_type == 'backgrounds':
            images = [all_images['backgrounds'][name][size]]
        elif image_type == 'floors':
            images = [all_images['floors'][name][size][view]]
        elif image_type in ['doors', 'chests', 'stairs', 'blockers']:
            if view:
                images = [all_images[image_type][name][view]]
            else:
                images = all_images[image_type][name]
        else:
            images = list(all_images[name].values())

        image_list = []
        for image in images:
            with open(image, 'r') as infile:
                image_list.append(infile.read())
    except Exception as e:
        print(f"{name=}\n{image_type=}\n{size=}\n{view}\n")
        raise e
    return image_list
