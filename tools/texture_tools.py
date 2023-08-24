import os
import glob
from PIL import Image

tga_texture_list = []
tga_texture_list.extend(glob.glob('*.TGA'))
tga_texture_list.extend(glob.glob('*.tga'))
print(tga_texture_list)

images = []
images.extend(glob.glob('*_MT_R_AO.png'))
images.extend(glob.glob('*_OcclusionRoughnessMetallic.png'))


def split_channels(image_file, image_name, extension='.png'):
    image_path = os.path.join(os.getcwd(), image_file)
    image = Image.open(image_path)

    r, g, b = image.split()
    r.save(image_name + '_metallic' + extension)
    g.save(image_name + '_roughness' + extension)
    b.save(image_name + '_ao' + extension)

def convert_to_png(image_file, image_name, extension='.png'):
    image_path = os.path.join(os.getcwd(), image_file)
    image = Image.open(image_path)

    image.save(image_name + extension)

def get_all_texture(extension_list=['png', 'tga', 'jpg']):
    texture_list = []

    for ext in extension_list:
        texture_list.extend(glob.glob('*.' + ext))
        texture_list.extend(glob.glob('*.' + ext.upper()))

    return texture_list

class Texture_Manager():
    """
    Texture Manager
    """
    base_color_name_list = str('diffuse diff albedo base col color basecolor').split(' ')
    subsurface_color_name_list = str('sss subsurface').split(' ')
    metallic_name_list = str('metallic metalness metal mtl mt').split(' ')
    specular_name_list = str('specularity specular spec spc').split(' ')
    roughness_name_list = str('roughness rough rgh r').split(' ')
    gloss_name_list = str('gloss glossy glossiness').split(' ')
    normal_name_list = str('normal nor nrm nrml norm n').split(' ')
    bump_name_list = str('bump bmp').split(' ')
    displacement_name_list = str('displacement displace disp dsp height heightmap').split(' ')
    trasmission_name_list = str('opacity').split(' ')
    alpha_name_list = str('alpha').split(' ')
    emission_name_list = str('emission').split(' ')

    def __init__(self, extension_list=['png', 'tga', 'jpg']):
        texture_list = get_all_texture(extension_list)

        for tex in texture_list:
            if ('_MT_R_AO' in tex) or ('_OcclusionRoughnessMetallic' in tex):
                self.split_texture(tex)
            else:
                self.rename_texture(tex)

    def split_texture(self, texture):
        channel = str(texture.split('.')[0]).split('_')[-1]
        name = '_'.join(str(texture.split('.')[0]).split('_')[:-1])

        split_channels(texture, name, extension='.png')

    def rename_texture(self, texture):
        channel = str(texture.split('.')[0]).split('_')[-1]
        name = '_'.join(str(texture.split('.')[0]).split('_')[:-1])

        print('Texture: ', texture, ' -- Name: ', name, ' -- Channel: ', channel)

        if channel.lower() in self.base_color_name_list:
            pass
        if channel.lower() in self.metallic_name_list:
            pass
        if channel.lower() in self.specular_name_list:
            pass
        if channel.lower() in self.roughness_name_list:
            pass
        if channel.lower() in self.gloss_name_list:
            pass
        if channel.replace('-OGL', '').lower() in self.normal_name_list:
            pass
        if channel.lower() in self.trasmission_name_list:
            pass
        if channel.lower() in self.displacement_name_list:
            pass



if __name__ == "__main__":
    #convert_all_textures()
    tx_manager = Texture_Manager()

    print('Done!')
    import time
    time.sleep(10)
