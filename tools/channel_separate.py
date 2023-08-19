import os
import glob
from PIL import Image

pattern1 = glob.glob('*_MT_R_AO.png')
pattern2 = glob.glob('*_OcclusionRoughnessMetallic.png')
images = []
images.extend(pattern1)
images.extend(pattern2)


def split_channels(image_file, image_name):
    image = Image.open(image_file)

    r, g, b = image.split()
    r.save(image_name + '_metallic.png')
    g.save(image_name + '_roughness.png')
    b.save(image_name + '_ao.png')

for img in images:
    image_path = os.path.join(os.getcwd(), img)
    print('Current Name: ', img)
    image_name = str(input('Replace base with: '))
    split_channels(image_path, image_name)
