from constants import BOX_SHAPE, CIRCLE_SHAPE
from utils import Point


class Asset:
    def __init__(self, asset_dict):
        self.id = asset_dict['id']
        self.name = asset_dict['name']
        self.footprint = int(asset_dict['footprint'])
        if self.id == 2 or self.id == 3:
            self.shape = CIRCLE_SHAPE
        else:
            self.shape = BOX_SHAPE


class Placement:
    def __init__(self, placement_dict, assets_dict):
        asset_id = placement_dict['assetId']
        asset_dict = assets_dict[asset_id - 1]
        self.asset = Asset(asset_dict)
        self.position = Point.dict_to_arr(placement_dict['position'])
        self.scale = Point.dict_to_arr(placement_dict['scale'])
        self.rotation = placement_dict['rotation']
