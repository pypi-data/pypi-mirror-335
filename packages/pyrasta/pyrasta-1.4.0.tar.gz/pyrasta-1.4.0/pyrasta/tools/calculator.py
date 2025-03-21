# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

import multiprocessing as mp
import numpy as np
from numba import jit

from pyrasta.tools import _gdal_temp_dataset, _return_raster, _clone_gdal_dataset
from pyrasta.tools.mapping import GDAL_TO_NUMPY
from pyrasta.utils import split_into_chunks
from tqdm import tqdm

try:
    from osgeo import gdal
except ImportError:
    import gdal

OP_WINDOW_SIZE = 1000


@jit(nopython=True, nogil=True)
def get_xy_block_windows(window_size, raster_x_size, raster_y_size):
    """ Get xy block window coordinates

    Description
    -----------
    Get xy block window coordinates depending
    on raster size and window size
    Used specifically for calculations. All windows are
    retrieved, whichever the size.

    Parameters
    ----------
    window_size: (int, int)
        size of window to read within raster as (width, height)
    raster_x_size: int
        raster's width
    raster_y_size: int
        raster's height

    Yields
    -------
    Window coordinates: tuple
        4-element tuple returning the coordinates of the window within the raster
    """

    for y in range(0, raster_y_size, window_size[1]):
        ysize = min(window_size[1], raster_y_size - y)
        for x in range(0, raster_x_size, window_size[0]):
            xsize = min(window_size[0], raster_x_size - x)

            yield x, y, xsize, ysize


@_return_raster
def _log(raster, out_file):

    out_ds = _clone_gdal_dataset(raster, out_file,
                                 gdal.GetDataTypeByName("float32"))

    for band in range(raster.nb_band):
        for window in get_xy_block_windows((OP_WINDOW_SIZE, OP_WINDOW_SIZE),
                                           raster.x_size,
                                           raster.y_size):

            array = raster._gdal_dataset.GetRasterBand(band + 1).\
                ReadAsArray(*window).astype("float32")
            out_ds.GetRasterBand(band + 1).WriteArray(np.log(array), window[0], window[1])

    # Close dataset
    out_ds = None


@_return_raster
def _log10(raster, out_file):

    out_ds = _clone_gdal_dataset(raster, out_file,
                                 gdal.GetDataTypeByName("float32"))

    for band in range(raster.nb_band):
        for window in get_xy_block_windows((OP_WINDOW_SIZE, OP_WINDOW_SIZE),
                                           raster.x_size,
                                           raster.y_size):

            array = raster._gdal_dataset.GetRasterBand(band + 1).\
                ReadAsArray(*window).astype("float32")
            out_ds.GetRasterBand(band + 1).WriteArray(np.log10(array), window[0], window[1])

    # Close dataset
    out_ds = None


@_return_raster
def _op(raster1, out_file, raster2, op_type):
    """ Basic arithmetic operations

    """
    out_ds = _clone_gdal_dataset(raster1, out_file,
                                 data_type=gdal.GetDataTypeByName('float32'))

    for band in range(1, raster1.nb_band + 1):

        for window in get_xy_block_windows((OP_WINDOW_SIZE, OP_WINDOW_SIZE),
                                           raster1.x_size,
                                           raster1.y_size):
            arrays = []
            for src in [raster1, raster2]:
                try:
                    arrays.append(src._gdal_dataset.GetRasterBand(
                        band).ReadAsArray(*window).astype("float32"))
                except AttributeError:
                    arrays.append(src)

            if op_type == "add":
                result = arrays[0] + arrays[1]
            elif op_type == "sub":
                result = arrays[0] - arrays[1]
            elif op_type == "rsub":
                result = arrays[1] - arrays[0]
            elif op_type == "mul":
                result = arrays[0] * arrays[1]
            elif op_type == "pow":
                result = arrays[0] ** arrays[1]
            elif op_type == "rpow":
                result = arrays[1] ** arrays[0]
            elif op_type == "truediv":
                result = np.full(arrays[0].shape, raster1.no_data)
                if not np.isscalar(arrays[1]):
                    result[arrays[1] != 0] = \
                        arrays[0][arrays[1] != 0] / arrays[1][arrays[1] != 0]
                else:
                    if arrays[1] != 0:
                        result = arrays[0] / arrays[1]
            elif op_type == "rtruediv":
                result = np.full(arrays[0].shape, raster1.no_data)
                result[arrays[0] != 0] = arrays[1] / arrays[0][arrays[0] != 0]
            else:
                result = None

            if np.isscalar(arrays[1]):
                result[arrays[0] == raster1.no_data] = raster1.no_data
            else:
                result[(arrays[0] == raster1.no_data) | (arrays[1] == raster2.no_data)] = \
                    raster1.no_data

            out_ds.GetRasterBand(band).WriteArray(result, window[0], window[1])

    # Close dataset
    out_ds = None


@_return_raster
def _raster_calculation(raster_class, out_file, gdal_driver, sources,
                        fhandle, window_size, input_type, output_type,
                        no_data, nb_processes, chunksize, description):
    """ Calculate raster expression

    """
    if not hasattr(window_size, "__getitem__"):
        window_size = (window_size, window_size)

    master_raster = sources[0]
    window_gen = ([src._gdal_dataset.ReadAsArray(*w).astype(GDAL_TO_NUMPY[input_type]) for src in
                   sources] for w in get_xy_block_windows(window_size,
                                                          master_raster.x_size,
                                                          master_raster.y_size))
    width = int(master_raster.x_size /
                window_size[0]) + min(1, master_raster.x_size % window_size[0])
    height = int(master_raster.y_size /
                 window_size[1]) + min(1, master_raster.y_size % window_size[1])

    # Initialization
    is_first_run = True
    y = 0

    if description:
        iterator = tqdm(split_into_chunks(window_gen, width),
                        total=height,
                        desc=description)
    else:
        iterator = split_into_chunks(window_gen, width)

    for win_gen in iterator:

        with mp.Pool(processes=nb_processes) as pool:
            list_of_arrays = list(pool.map(fhandle,
                                           win_gen,
                                           chunksize=chunksize))

        result = np.concatenate(list_of_arrays, axis=list_of_arrays[0].ndim - 1)

        if is_first_run:
            if result.ndim == 2:
                nb_band = 1
            else:
                nb_band = result.shape[0]

            out_ds = _gdal_temp_dataset(out_file,
                                        gdal_driver,
                                        master_raster._gdal_dataset.GetProjection(),
                                        master_raster.x_size,
                                        master_raster.y_size, nb_band,
                                        master_raster.geo_transform,
                                        output_type,
                                        no_data)

            is_first_run = False

        if nb_band == 1:
            out_ds.GetRasterBand(1).WriteArray(result, 0, y)
        else:
            for band in range(nb_band):
                out_ds.GetRasterBand(band + 1).WriteArray(result[band, :, :],
                                                          0, y)

        y += window_size[1]

    # Close dataset
    out_ds = None
