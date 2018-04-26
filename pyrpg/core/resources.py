from pkg_resources import resource_listdir, resource_filename


def list_maps():
    print(resource_listdir('pyrpg.assets.maps', ''))


def list_data():
    print(resource_listdir('pyrpg.assets.data', ''))


def get_data_asset(name):
    return resource_filename('pyrpg.assets.data', name)


def get_map_asset(name):
    return resource_filename('pyrpg.assets.maps', name)


def get_image_asset(name):
    return resource_filename("pyrpg.assets.images", name)


def get_font_asset(name):
    return resource_filename("pyrpg.assets.fonts", name)


def get_sound_asset(name):
    return resource_filename("pyrpg.assets.sounds", name)

