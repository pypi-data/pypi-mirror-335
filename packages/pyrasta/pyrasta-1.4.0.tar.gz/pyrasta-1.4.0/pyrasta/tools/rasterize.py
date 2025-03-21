# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
from pyrasta.io_ import GEOJSON_DRIVER
from pyrasta.io_.files import GeojsonTempFile
from pyrasta.tools import _gdal_temp_dataset, _return_raster

from pyrasta.utils import gdal_progress_bar

try:
    from osgeo import gdal
except ImportError:
    import gdal


@_return_raster
def _rasterize(raster_class, out_file, gdal_driver, geodataframe,
               burn_values, attribute, x_size, y_size,
               nb_band, geo_transform, out_data_type, no_data, all_touched,
               progress_bar):
    """ Rasterize geographic layer

    Parameters
    ----------
    raster_class: RasterBase
        Raster class to return
    out_file: str
        Output file to which raster is written
    gdal_driver: gdal.Driver
        GDAL driver
    geodataframe: geopandas.GeoDataFrame or gistools.layer.GeoLayer
        Geographic layer to be rasterized
    burn_values: None or list[float] or list[int]
        list of values to burn in each band, excusive with attribute
    attribute: str
        attribute in layer from which burn value must be retrieved
    x_size: int
    y_size: int
    nb_band: int
    geo_transform: tuple
    out_data_type
    no_data
    all_touched: bool
    progress_bar: bool

    Returns
    -------

    """

    with GeojsonTempFile() as geojson_file:

        geodataframe.to_file(geojson_file.path, driver=GEOJSON_DRIVER)

        out_ds = _gdal_temp_dataset(out_file,
                                    gdal_driver,
                                    geodataframe.crs.to_wkt(),
                                    x_size,
                                    y_size,
                                    nb_band,
                                    geo_transform,
                                    out_data_type,
                                    no_data)

        callback, callback_data = gdal_progress_bar(progress_bar,
                                                    description="Rasterize layer")

        gdal.Rasterize(out_ds,
                       geojson_file.path,
                       bands=[bd + 1 for bd in range(nb_band)],
                       burnValues=burn_values,
                       attribute=attribute,
                       allTouched=all_touched,
                       callback=callback,
                       callback_data=callback_data)

    out_ds = None

    # Be careful with the temp file, make a pointer to be sure
    # the Python garbage collector does not destroy it !
    # raster = raster_class(out_file.path)
    # raster._temp_file = out_file
    #
    # return raster
