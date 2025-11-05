import glob
from pathlib import Path

from PIL import Image


def gamma_correction(img, gamma):
    """Apply gamma correction to an image.

    Args:
        img: PIL Image object
        gamma: Gamma correction value

    Returns:
        PIL Image object with gamma correction applied
    """
    img_out = img.point(lambda x: ((x / 255) ** gamma) * 255)
    return img_out

def colorspace_conversion(img, colorspace='None', gamma_to_srgb=2.2, gamma_to_linear=0.454545):
    """Convert image between color spaces with gamma correction.

    Args:
        img (PIL.Image): Image to convert.
        colorspace (str): Target colorspace: 'None', 'sRGB', or 'linear'.
        gamma_to_srgb (float): Gamma value for sRGB correction.
        gamma_to_linear (float): Gamma value for linear correction.

    Returns:
        PIL.Image: Image with colorspace conversion applied.
    """
    if colorspace == 'None':
        print(check_colorspace(img))
        return img
    elif colorspace == 'sRGB':
        return gamma_correction(img, gamma_to_srgb)
    elif colorspace == 'linear':
        return gamma_correction(img, gamma_to_linear)
    else:
        print('Invalid colorspace')
        return img

def check_colorspace(img):
    """Detect image color space from ICC profile.

    Args:
        img (PIL.Image): Image to check.

    Returns:
        str: Detected colorspace: 'sRGB', 'linear', or 'Unknown'.
    """
    icc_profile = img.info.get('icc_profile')

    if icc_profile:
        if b'sRGB' in icc_profile:
            return 'sRGB'
        else:
            return 'linear'
    else:
        return 'Unknown'

def split_channels(image_file, image_name, extension='.png', colorspace='None'):
    """Split RGB channels into separate files (metallic, roughness, AO).

    Args:
        image_file (str): Path to input image.
        image_name (str): Base name for output files.
        extension (str): Output file extension.
        colorspace (str): Colorspace for conversion.
    """
    image_path = Path(image_file)
    if not image_path.is_absolute():
        image_path = Path.cwd() / image_path
    with Image.open(image_path) as src_image:
        converted = colorspace_conversion(src_image, colorspace)
        r_channel, g_channel, b_channel = converted.split()
        r_channel.save(image_name + '_metallic' + extension)
        g_channel.save(image_name + '_roughness' + extension)
        b_channel.save(image_name + '_ao' + extension)

def convert_to_png(image_file, image_name, extension='.png', colorspace='None'):
    """Convert image to PNG format with optional colorspace conversion.

    Args:
        image_file (str): Path to input image.
        image_name (str): Base name for output file.
        extension (str): Output file extension.
        colorspace (str): Colorspace for conversion.
    """
    image_path = Path(image_file)
    if not image_path.is_absolute():
        image_path = Path.cwd() / image_path
    with Image.open(image_path) as src_image:
        converted = colorspace_conversion(src_image, colorspace)
        converted.save(image_name + extension)

def get_all_texture(extension_list=None):
    """Find all texture files in current directory with specified extensions.

    Args:
        extension_list (tuple): File extensions to search for (case-insensitive).

    Returns:
        set: Unique set of matching texture file names.
    """
    if extension_list is None:
        extension_list = ('png', 'tga', 'jpg')
    texture_list = []

    for ext in extension_list:
        texture_list.extend(glob.glob('*.' + ext))
        texture_list.extend(glob.glob('*.' + ext.upper()))

    return set(texture_list)

class TextureManager:
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
    transmission_name_list = str('opacity').split(' ')
    alpha_name_list = str('alpha').split(' ')
    emission_name_list = str('emission').split(' ')

    def __init__(self, extension='.png', extension_search_list=None):
        self.extension = extension
        if extension_search_list is None:
            extension_search_list = ('png', 'tga', 'jpg')
        self.texture_list = get_all_texture(extension_search_list)

        for tex in self.texture_list:
            if ('_MT_R_AO' in tex) or ('_OcclusionRoughnessMetallic' in tex):
                self.split_texture(tex)
            else:
                self.rename_texture(tex)

    def split_texture(self, texture):
        """Split packed texture into separate channel files.

        Args:
            texture (str): Packed texture filename.
        """
        name = str(texture.split('.')[0])
        name = name.replace('_MT_R_AO', '').replace('_OcclusionRoughnessMetallic', '')

        split_channels(texture, name, extension='.png')

    def rename_texture(self, texture):
        """Rename texture file based on channel type detection.

        Args:
            texture (str): Texture filename to process.
        """
        channel = str(texture.split('.')[0]).split('_')[-1]
        name = '_'.join(str(texture.split('.')[0]).split('_')[:-1])

        print(f'Texture: {texture} -- Name: {name} -- Channel: {channel}')

        channel_lower = channel.lower()
        normalized_channel = channel_lower.replace('-ogl', '')

        channel_mappings = (
            (self.base_color_name_list, '_diffuse', channel_lower),
            (self.metallic_name_list, '_metallic', channel_lower),
            (self.subsurface_color_name_list, '_subsurface', channel_lower),
            (self.specular_name_list, '_specular', channel_lower),
            (self.roughness_name_list, '_roughness', channel_lower),
            (self.gloss_name_list, '_gloss', channel_lower),
            (self.normal_name_list, '_normal', normalized_channel),
            (self.transmission_name_list, '_transmission', channel_lower),
            (self.alpha_name_list, '_opacity', channel_lower),
            (self.emission_name_list, '_emission', channel_lower),
            (self.displacement_name_list, '_displacement', channel_lower),
        )

        for names, suffix, candidate in channel_mappings:
            if candidate in names:
                convert_to_png(texture, name + suffix, self.extension)



if __name__ == "__main__":
    tx_manager = TextureManager()
    print('Done!')
