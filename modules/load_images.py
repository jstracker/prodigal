import yaml
import path


with open('images/all_images.yml', 'r') as infile:
    all_images = yaml.safe_load(infile)

def load_image(image_name):
    pass
