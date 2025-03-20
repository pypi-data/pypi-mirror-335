from typing import Tuple
import numpy as np
from osgeo import gdal
import os


def ReadGeoTiff(file_name: str) -> Tuple[np.ndarray, Tuple[float, float, float, float, float, float], str]:
    """
    Reads a GeoTIFF file and returns the image data, geotransformation parameters, and projection information.

    Parameters:
        file_name (str): Path to the input GeoTIFF file.

    Returns:
        Tuple[np.ndarray, Tuple[float, float, float, float, float, float], str]:
        - im_data: Image data as a NumPy array.
        - im_geotrans: Geotransformation parameters (tuple of 6 floats).
        - im_proj: Projection information as a string.

    Raises:
        FileNotFoundError: If the file cannot be opened or does not exist.
    """
    dataset = gdal.Open(file_name)
    if dataset is None:
        raise FileNotFoundError(f"File {file_name} cannot be opened or does not exist.")

    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)
    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()

    return im_data, im_geotrans, im_proj


def CreateGeoTiff(
        out_raster: str,
        image: np.ndarray,
        geo_transform: Tuple[float, float, float, float, float, float],
        projection: str,
        dtype: str = "float",
        compress: bool = False
) -> None:
    """
    Creates a GeoTIFF file.

    Parameters:
        out_raster (str): Path to the output GeoTIFF file.
        image (np.ndarray): Image data as a NumPy array.
        geo_transform (Tuple[float, float, float, float, float, float]): Geotransformation parameters (tuple of 6 floats).
        projection (str): Projection information in WKT format.
        dtype (str, optional): Data type, defaults to 'float'. Options: 'int16', 'int32', 'float'.
        compress (bool, optional): Whether to apply LZW lossless compression, defaults to False.

    Returns:
        None

    Raises:
        ValueError: If the image data shape is invalid.
        IOError: If the GeoTIFF file cannot be created.
    """

    dtype_mapping = {"int16": gdal.GDT_Int16, "int32": gdal.GDT_Int32, "float": gdal.GDT_Float32}
    gdal_dtype = dtype_mapping.get(dtype, gdal.GDT_Float32)

    # 获取影像维度
    shape = image.shape
    if len(shape) == 2:
        bands, rows, cols = 1, *shape
    elif len(shape) == 3:
        bands, rows, cols = shape
    else:
        raise ValueError("Invalid image data format. Expected shape (H, W) or (C, H, W).")

    # 创建数据集
    driver = gdal.GetDriverByName("GTiff")
    options = ["TILED=YES", f"COMPRESS=LZW"] if compress else []
    dataset = driver.Create(out_raster, cols, rows, bands, gdal_dtype, options=options)

    if dataset is None:
        raise IOError(f"Failed to create GeoTIFF file: {out_raster}")

    dataset.SetGeoTransform(geo_transform)
    dataset.SetProjection(projection)

    # 写入数据
    if bands == 1:
        dataset.GetRasterBand(1).WriteArray(image)
    else:
        for i in range(bands):
            dataset.GetRasterBand(i + 1).WriteArray(image[i])

    # 释放资源
    del dataset


def CompressGeoTiff(path: str, method: str = "LZW") -> None:
    """
       Compresses a GeoTIFF file using GDAL.

       Parameters:
           path (str): Path to the GeoTIFF file to be compressed.
           method (str, optional): Compression method, defaults to 'LZW' (lossless compression).

       Returns:
           None

       Raises:
           FileNotFoundError: If the specified file does not exist.
           IOError: If the file cannot be opened.
       """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} does not exist.")

    dataset = gdal.Open(path)
    if dataset is None:
        raise IOError(f"Failed to open file: {path}")

    driver = gdal.GetDriverByName("GTiff")
    target_path = path.replace(".tif", "_compressed.tif")

    compressed_dataset = driver.CreateCopy(target_path, dataset, strict=1, options=["TILED=YES", f"COMPRESS={method}"])
    del dataset, compressed_dataset
