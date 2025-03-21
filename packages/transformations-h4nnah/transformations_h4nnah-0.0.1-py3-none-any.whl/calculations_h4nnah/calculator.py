from pyproj import Transformer


def wgs84_to_lest97(latitude, longitude):
    """Teisendab WGS84 koordinaadid (laiuskraad, pikkuskraad) L-Est97 koordinaatideks (X, Y)."""

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3301", always_xy=True)
    x, y = transformer.transform(longitude, latitude)
    return x, y


def lest97_to_wgs84(x, y):
    """Teisendab L-Est97 koordinaadid (X, Y) WGS84 koordinaatideks (laiuskraad, pikkuskraad)."""

    transformer = Transformer.from_crs("EPSG:3301", "EPSG:4326", always_xy=True)
    longitude, latitude = transformer.transform(x, y)
    return latitude, longitude
