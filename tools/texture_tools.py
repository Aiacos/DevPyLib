import os
import glob
from PIL import Image, ImageFilter


def gamma_correction(img, gamma):
    #LUT = ImageFilter.Color3DLUT.generate((11, 11, 11), lambda r, g, b: (r ** gamma, g ** gamma, b ** gamma))
    #img_out = img.filter(LUT)
    img_out = img.point(lambda x: ((x / 255) ** gamma) * 255)

    return img_out

def colorspace_conversion(img, colorspace='None', gamma_to_srgb=2.2, gamma_to_linear=0.454545):
    if colorspace == 'None':
        return img
    elif colorspace == 'sRGB':
        return gamma_correction(img, gamma_to_srgb)
    elif colorspace == 'linear':
        return gamma_correction(img, gamma_to_linear)
    else:
        print('Invalid colorspace')
        return img


def split_channels(image_file, image_name, extension='.png', colorspace='None'):
    image_path = os.path.join(os.getcwd(), image_file)
    image = Image.open(image_path)

    image = colorspace_conversion(image, colorspace)

    r, g, b = image.split()
    r.save(image_name + '_metallic' + extension)
    g.save(image_name + '_roughness' + extension)
    b.save(image_name + '_ao' + extension)

def convert_to_png(image_file, image_name, extension='.png', colorspace='None'):
    image_path = os.path.join(os.getcwd(), image_file)
    image = Image.open(image_path)

    image = colorspace_conversion(image, colorspace)

    image.save(image_name + extension)

def get_all_texture(extension_list=['png', 'tga', 'jpg']):
    texture_list = []

    for ext in extension_list:
        texture_list.extend(glob.glob('*.' + ext))
        texture_list.extend(glob.glob('*.' + ext.upper()))

    return set(texture_list)

class Texture_Manager():
    """
    Texture Manager
    """
    base_color_name_list = str('diffuse diff albedo base col color basecolor bc').split(' ')
    subsurface_color_name_list = str('sss subsurface').split(' ')
    metallic_name_list = str('metallic metalness metal mtl mt').split(' ')
    specular_name_list = str('specularity specular spec spc').split(' ')
    roughness_name_list = str('roughness rough rgh').split(' ')
    gloss_name_list = str('gloss glossy glossiness').split(' ')
    normal_name_list = str('normal nor nrm nrml norm n').split(' ')
    bump_name_list = str('bump bmp').split(' ')
    displacement_name_list = str('displacement displace disp dsp height heightmap').split(' ')
    trasmission_name_list = str('opacity').split(' ')
    alpha_name_list = str('alpha').split(' ')
    emission_name_list = str('emission').split(' ')

    def __init__(self, extension='.png', extension_search_list=['png', 'tga', 'jpg']):
        self.extension = extension
        self.texture_list = get_all_texture(extension_search_list)

        for tex in self.texture_list:
            if ('_MT_R_AO' in tex) or ('_OcclusionRoughnessMetallic' in tex):
                self.split_texture(tex)
            else:
                self.rename_texture(tex)

    def split_texture(self, texture):
        channel = str(texture.split('.')[0]).split('_')[-1]
        name = str(texture.split('.')[0])
        name = name.replace('_MT_R_AO', '').replace('_OcclusionRoughnessMetallic', '')

        split_channels(texture, name, extension='.png')

    def rename_texture(self, texture):
        channel = str(texture.split('.')[0]).split('_')[-1]
        name = '_'.join(str(texture.split('.')[0]).split('_')[:-1])

        print('Texture: ', texture, ' -- Name: ', name, ' -- Channel: ', channel)

        if channel.lower() in self.base_color_name_list:
            convert_to_png(texture, name + '_diffuse', self.extension)
        if channel.lower() in self.metallic_name_list:
            convert_to_png(texture, name + '_metallic', self.extension)
        if channel.lower() in self.subsurface_color_name_list:
            convert_to_png(texture, name + '_subsurface', self.extension)
        if channel.lower() in self.specular_name_list:
            convert_to_png(texture, name + '_specular', self.extension)
        if channel.lower() in self.roughness_name_list:
            convert_to_png(texture, name + '_roughness', self.extension)
        if channel.lower() in self.gloss_name_list:
            convert_to_png(texture, name + '_gloss', self.extension)
        if channel.replace('-OGL', '').lower() in self.normal_name_list:
            convert_to_png(texture, name + '_normal', self.extension)
        if channel.lower() in self.trasmission_name_list:
            convert_to_png(texture, name + '_trasmission', self.extension)
        if channel.lower() in self.alpha_name_list:
            convert_to_png(texture, name + '_opacity', self.extension)
        if channel.lower() in self.emission_name_list:
            convert_to_png(texture, name + '_emission', self.extension)
        if channel.lower() in self.displacement_name_list:
            convert_to_png(texture, name + '_displacement', self.extension)



if __name__ == "__main__":
    #convert_all_textures()
    tx_manager = Texture_Manager()

    print('Done!')
    import time
    time.sleep(10)
