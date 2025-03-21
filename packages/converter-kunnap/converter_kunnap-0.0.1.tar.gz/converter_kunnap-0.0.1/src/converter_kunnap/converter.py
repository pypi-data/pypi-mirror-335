from pyproj import Transformer

def wgs84_to_l_est97(lon, lat):
    return Transformer.from_crs("EPSG:4326", "EPSG:3301", always_xy=True).transform(lon, lat)

def l_est97_to_wgs84(x, y):
    return Transformer.from_crs("EPSG:3301", "EPSG:4326", always_xy=True).transform(x, y)
