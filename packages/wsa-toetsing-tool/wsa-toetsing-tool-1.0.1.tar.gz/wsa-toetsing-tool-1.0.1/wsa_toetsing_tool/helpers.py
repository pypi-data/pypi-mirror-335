import os
import shutil
import tqdm
import logging
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from osgeo import gdal
from psutil import virtual_memory
from shapely.geometry import Point
from rasterio.mask import mask
from rasterio import features
from shapely.geometry import box
from pathlib import Path

from wsa_toetsing_tool.config import CACHELIMIT, MEMORYLIMIT

def set_crs(obj, crs="EPSG:28992"):
    """
    Function that checks if the given object (geodataframe or rasterio raster)
    """
    if obj.crs is None:
        #obj.crs = crs
        raise Exception(f"No projection defined for object {obj}")
    elif str.upper(obj.crs.srs) != crs:
        obj = obj.to_crs(crs)
    else:
        obj.crs = crs
    return obj


def set_gdal_cache_limit(gdal_cachemax=None):
    if gdal_cachemax is None:
        mem = virtual_memory()
        gdal_cachemax = int(CACHELIMIT * mem.free * 1e-6)
    gdal.SetConfigOption('GDAL_CACHEMAX', str(gdal_cachemax))
    print(f"GDAL_CACHEMAX set to {gdal_cachemax}mb")
    return


def mosaic_raster(fnames: list, filename: str, export_folder: str, clip_polygon: str, cachelimit: int = None,
                  memorylimit=None, file_extension="tif"):
    """
    Mosaic geotiffs using GDAL warp which makes is possible to limit the memory use. This is required for raster larger than the systems memory.
    Args:
        fnames: list of filenames. Note that zip files has a unique notition starting with '/vsizip/'
        filename: name of the export file
        export_folder: folder to export the raster to

    Returns: filename of the output raster

    """

    def progress_callback(complete, message, unknown):
        pbar.update(complete)
        return 1

    print(f"Mosaic raster with GDAL")

    if file_extension == "tif":
        co = ["TILED=YES"]
    else:
        co = None

    if clip_polygon is None:
        crop = False
    else:
        crop = True

    # set_gdal_cache_limit(cachelimit)

    fname_output = os.path.join(export_folder, filename + "." + file_extension)
    with tqdm.tqdm(total=1) as pbar:
        ds = gdal.Warp(fname_output, fnames, copyMetadata=True, warpMemoryLimit=get_memorylimit(memorylimit),
                       multithread=False, callback=progress_callback, callback_data=pbar, cropToCutline=crop,
                       cutlineDSName=clip_polygon, creationOptions=co)
        ds = None
    return fname_output


def get_memorylimit(memorylimit=None):
    if memorylimit is None:
        mem = virtual_memory()
        memorylimit = int(MEMORYLIMIT * mem.free * 1e-6)
    return memorylimit


def point(df, x: str = 'X', y: str = 'Y'):
    """Add geometry col to df as a POINT object"""
    return [Point(xi, yi) for xi, yi in zip(df[x], df[y])]


def fn_correct_capitals(file_path):
    # Correct filename if the capitals in the filename (not filepath) are wrong
    file_list = os.listdir(os.path.dirname(file_path))
    file_list_lower = [fn.lower() for fn in file_list]

    if str.lower(os.path.basename(file_path)) in file_list_lower:
        index = file_list_lower.index(str.lower(os.path.basename(file_path)))
        return os.path.join(os.path.dirname(file_path), file_list[index])
    else:
        raise Exception('file not found:' + file_path)

def remove_folder_and_files(folder):
    """
    Remove the folder including its contents
    """
    shutil.rmtree(folder)


def realign_raster_to_reference(
    reference_rst, raster_to_align
):
    with rasterio.open(raster_to_align) as rio_align:
        with rasterio.open(reference_rst) as rio_ref:
            profile = rio_ref.profile
            depth_bounds_poly = box(
                rio_align.bounds[0], rio_align.bounds[1], rio_align.bounds[2], rio_align.bounds[3]
            )
            interest_bounds = box(
                rio_ref.bounds[0],
                rio_ref.bounds[1],
                rio_ref.bounds[2],
                rio_ref.bounds[3],
            )
            shared_bbox = [depth_bounds_poly.intersection(interest_bounds)]

            clipped_align, clipped_align_transform = mask(
                rio_align, shared_bbox, crop=True
            )
            clipped_ref, clipped_ref_transform = mask(
                rio_ref, shared_bbox, crop=False
            )
            profile["transform"] = clipped_ref_transform
            destination = np.zeros(np.shape(clipped_ref), np.float32)

            # Get nodata values
            nodata_align = rio_align.nodata
            nodata_ref = rio_ref.nodata

            # Replace nodata values in clipped_align with nodata_ref
            if nodata_align is not None and nodata_ref is not None:
                clipped_align = np.where(clipped_align == nodata_align, nodata_ref, clipped_align)

            (
                reprojected_rst,
                reprojected_rst_transform,
            ) = rasterio.warp.reproject(
                source=clipped_align,
                destination=destination,
                src_crs=rio_align.crs,
                src_transform=clipped_align_transform,
                dst_transform=clipped_ref_transform,
                dst_crs=rio_ref.crs,
            )

            realigned_rst = reprojected_rst.squeeze()

            profile["width"] = np.shape(realigned_rst)[1]
            profile["height"] = np.shape(realigned_rst)[0]

            return realigned_rst, profile


def clip_raster_to_shape(raster, shape, export_folder=None):
    """
    Clip raster boundary of a shape
    return the filename of the new raster
    """

    shp = gpd.read_file(shape)

    with rasterio.open(raster) as rst:
        if shp.unary_union.bounds == tuple(rst.bounds):
            return raster
        else:
            out_image, out_transform = rasterio.mask.mask(
                rst, [shp.unary_union], crop=True)
            out_meta = rst.meta
            out_meta.update({"driver": "GTiff",
                            "height": out_image.shape[1],
                             "width": out_image.shape[2],
                             "transform": out_transform})
            if export_folder is not None:
                fn_export = os.path.join(export_folder, os.path.basename(raster))
            
            fn_export = fn_export.replace(".tif", "_clipped.tif")

            with rasterio.open(fn_export, "w", **out_meta) as dest:
                dest.write(out_image)
            return fn_export


def validate_raster_input(raster, ref_raster, export_folder=None):
    """
    valdate if the raster is aligned to the reference raster. If not, the raster is realigned
    return: 
    """
    validate_input([raster])

    with rasterio.open(raster) as rst:
        with rasterio.open(ref_raster) as rst_ref:
            if tuple(rst.bounds) == tuple(rst_ref.bounds):
                return raster

    realigned_rst, profile = realign_raster_to_reference(
        reference_rst=ref_raster, raster_to_align=raster)

    
    if export_folder is not None:
        fn_export = os.path.join(export_folder, os.path.basename(raster))
    else:
        fn_export = raster
    fn_export = fn_export.replace(".tif", "_aligned.tif")
    with rasterio.open(fn_export, "w", **profile) as dest:
        dest.write(realigned_rst, 1)
    print(f"Raster realigned and saved to: {fn_export}")
    return fn_export


def validate_input(fn_input: list):
    file_list = []
    for file in fn_input:
        if type(file) == dict:
            file_list = file_list + list(file.values())
        if type(file) == list:
            file_list = file_list + file
        else:
            pass

    for file in file_list:
        if os.path.exists(file):
            print(f'{file} found')
        else:
            raise NameError(
                f'ERROR {file} not found. Please check your input!')

def validate_crs(fn_input):
    gdf = gpd.read_file(fn_input)
    if gdf.crs is None:
        raise Exception(f"No projection system is defined in file {fn_input}")

def validate_columns_in_shp(file, columns: list):
    validate_input([file])
    gdf = gpd.read_file(file)
    for col in columns:
        if col not in gdf.columns:
            raise NameError(
                f"Column {col} doet not exist in {file}. The columns in the file are: {list(gdf.columns)}")


def add_geometry_to_df(df, gdf):
    # in pycharm replace nodes with network
    df = pd.concat([df, gdf['geometry']], axis=1)
    gdf_gumbel = gpd.GeoDataFrame(
        df.dropna(subset=['geometry']), geometry='geometry')
    gdf_gumbel.crs = 'EPSG:28992'
    return gdf_gumbel


def create_dir(dir):
    """
    Create directory if not exists
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.info(f'directory created {dir}')
    else:
        logging.info(
            f'Directory already exists. Files will possibly be overwritten: {dir}')
    return os.path.abspath(dir)


def gdf_to_raster(gdf, value_col, rst_reference, filename_output):
    """
    Convert gdf to raster and realign
    Args:
        gdf: geodataframe met polygonen
        value_col: kolom met waarden (int of float)
        rst_reference: referentieraster voor alignment
        filename_output: ouput bestandsnaam

    Returns:

    """
    with rasterio.open(rst_reference, 'r') as EM:
        transform = EM.transform
        profile = EM.profile
        out_shape = EM.shape

    if value_col is not None:
        shapes = list(zip(gdf.geometry, gdf[value_col]))
    else:
        shapes = list(gdf.geometry)

    rst = features.rasterize(
        shapes=shapes, out_shape=out_shape, transform=transform, fill=profile["nodata"])

    Path(filename_output).parent.mkdir(parents=True, exist_ok=True)
    fn_output_tmp = filename_output.replace(".tif", "_tmp.tif")

    with rasterio.open(fn_output_tmp, 'w', **profile) as out:
        out.write_band(1, rst.astype(profile['dtype']))

    realigned_rst, profile_aligned = realign_raster_to_reference(
        rst_reference, fn_output_tmp)
    profile_aligned["compress"] = "lzw"
    with rasterio.open(filename_output, 'w', **profile_aligned) as out:
        out.write_band(1, realigned_rst.astype(profile['dtype']))

    os.remove(fn_output_tmp)
    return filename_output


def bgt_functie_to_rst(bgt_shp, filename_output, reference_raster, bgt_col_functie="FUNCTIE",
                       bgt_functie_objecttypen=["waterloop", "watervlak"]):
    """Zet bgt shape om naar een raster met waarden 1 voor gekozen functietypen"""
    print(
        f"Genereer raster op basis van {bgt_shp} en de functies {str(bgt_functie_objecttypen)}")
    bgt_water = gpd.read_file(bgt_shp)
    bgt_water = bgt_water.to_crs("EPSG:28992")
    bgt_water = bgt_water[bgt_water[bgt_col_functie].isin(
        bgt_functie_objecttypen)]
    
    gdf_to_raster(bgt_water, None, reference_raster, filename_output)
    print(f"Raster opgeslagen: {filename_output}")
    return filename_output

def validate_overlap_KAE_PG(kae, pg, output_file, threshold=0.01):
    """
    Valideert dat kleinste afwateringsgebieden (KAE) binnen een peilgebied (PG) vallen met een bepaalde threshold. Wanneer
    de treshold 0.01 is wordt een error afgegeven wanneer een KAE meer dan 1 % overlapt en minder dan 99% overlapt met
    een bepaald peilgebied.
    """

    pg = pg.copy()
    pg['geometry_PG'] = pg.geometry
    joined = gpd.sjoin(kae, pg, how="left", predicate='intersects', lsuffix='KAE', rsuffix='PG')
    joined['intersection_area'] = joined.apply(lambda x: x['geometry'].intersection(x['geometry_PG']).area, axis=1)
    joined['intersection_fraction'] = joined['intersection_area'] / joined.geometry.area
    mismatch = joined[(joined['intersection_fraction'] > threshold) & (joined['intersection_fraction'] < 1-threshold)]
    mismatch = mismatch.drop(columns=['geometry_PG'])
    if len(mismatch) > 0:
        if output_file:
            mismatch.to_file(output_file)
        raise Exception(f"Kleinste afwateringsgebieden overlappen met meerdere peilgebieden buiten de marge van {threshold*100}%. Shapefile met de afwateringsgebieden in kwestie weggeschreven naar {output_file}")

def export_max_wl_to_csv(df, fn):

    return None

def copy_fou_to_test(from_path, to_path):
    source_dir = Path(from_path)
    target_file_name = "*_fou.nc"

    fou_files = []
    for file in source_dir.rglob(target_file_name):
        fou_files.append(file)
        file_id = file.parents[2].name
        to_file = Path(to_path) / file_id / file.name
        to_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(file,to_file)

if __name__ == '__main__':
    from_path = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\input\model\Output'
    to_path = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\tests\data\input\dhydro'
    copy_fou_to_test(from_path, to_path)