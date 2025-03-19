from netCDF4 import Dataset
import pandas as pd
import geopandas as gpd
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
from tqdm import tqdm

def array_to_str(ar):
    """
    Returns a string based on a list of bytes
    Args:
        ar: array

    Returns: string
    """

    return "".join(str(s, encoding="UTF-8").strip() for s in ar)


def fou_series_to_gdf(result_folder, max_wl_var, max_wl_time_var=None):
    """
    Reads all *_fou.nc files in (subdirectories of) the result_folder, reads the maximum water level and the time of
    occurence or start date of the statistic analysis. Combines all entries in a single dataframe df_stat. Also returns a GeoDataFrame with the node id's and
    point geometry

    Args:
        result_folder: Folder containing *_fou.nc files, files can be in subfolders
        max_wl_var: Name of the variable of the maximum water level statistics in the *_fou.nc files
        max_wl_time_var: Name of the variable of the time of occurence of the maximum water level statistics in the *_fou.nc files

    Returns: DataFrame containing stats + GeoDataFrame containing network
    """
    source_dir = Path(result_folder)
    target_file_name = "*_fou.nc"

    fou_files = []
    for file in source_dir.rglob(target_file_name):
        print(file)
        fou_files.append(file)

    print(f'Aantal gevonden *_fou.nc files: {len(fou_files)}')

    df_stat = pd.DataFrame()
    gdf_fou = None
    for fn_fou in tqdm(fou_files, desc="Reading .fou files"):
        df_fou, gdf_fou = fou_to_gdf(fn_fou, max_wl_var=max_wl_var, max_wl_time_var=max_wl_time_var)
        df_stat = pd.concat([df_stat, df_fou])

    #add max_wl_var as first index
    df_stat.columns = pd.MultiIndex.from_product([[max_wl_var], df_stat.columns])
    df_stat.index.name = None

    return df_stat, gdf_fou

def fou_to_gdf(fn_fou, max_wl_var, max_wl_time_var=None, crs='EPSG:28992'):
    """
    Reads a *_fou.nc file, reads the maximum water level and the time of occurence or start date of the statistic analysis. Combines all entries in a single dataframe df_stat. Also returns a GeoDataFrame with the node id's and
    point geometry.

    Args:
        result_folder: Folder containing *_fou.nc files, files can be in subfolders
        max_wl_var: Name of the variable of the maximum water level statistics in the *_fou.nc files
        max_wl_time_var: Name of the variable of the time of occurence of the maximum water level statistics in the *_fou.nc files

    Returns: DataFrame containing stats + GeoDataFrame containing network
    """
    ds = Dataset(fn_fou)

    # read nodes
    nodes = ds.variables['mesh1d_node_id']
    node_list = []
    for i in range(len(nodes)):
        node_list.append(array_to_str(nodes[i, :].data))

    # Read maximum water levels
    try:
        wl_list = list(ds.variables[max_wl_var][:].data)
    except KeyError:
        raise KeyError(f"Variabele {max_wl_var} bestaat niet in {fn_fou}. Kies uit de volgende variabelen: {list(ds.variables.keys())}")

    # Read geometries
    x_list = list(ds.variables['mesh1d_node_x'][:].data)
    y_list = list(ds.variables['mesh1d_node_y'][:].data)

    if max_wl_time_var is not None:
        # Read occurence time of maximum water level
        time_list = list(ds.variables[max_wl_time_var][:].data) #unit in seconds since reference time
        ref_date_int = ds.variables[max_wl_time_var].reference_date_in_yyyymmdd
        ref_date = datetime.strptime(str(ref_date_int), '%Y%m%d')
        datetime_list = [ref_date + timedelta(seconds=seconds) if seconds >= 0 else np.nan for seconds in time_list]

        dict_maxwl = {'id': node_list, max_wl_time_var: datetime_list, max_wl_var: wl_list, 'x': x_list, 'y': y_list}
        df_maxwl = pd.DataFrame(dict_maxwl)
        df_maxwl = df_maxwl.pivot(index=max_wl_time_var, columns='id', values=max_wl_var)
    else:
        # Read start of statistics
        ref_date_int = ds.variables[max_wl_var].reference_date_in_yyyymmdd
        ref_date = datetime.strptime(str(ref_date_int), '%Y%m%d')
        dt_stat_start = ref_date + timedelta(minutes=ds.variables[max_wl_var].starttime_min_max_analysis_in_minutes_since_reference_date)
        datetime_list = [dt_stat_start]
        df_maxwl = pd.DataFrame([wl_list], index=datetime_list, columns=node_list)

    df_network = pd.DataFrame({'x': x_list, 'y': y_list}, index=node_list)
    gdf_network = gpd.GeoDataFrame(df_network, geometry=gpd.points_from_xy(df_network.x, df_network.y), crs=crs)

    return df_maxwl, gdf_network

def get_calculation_points(fn_fou):
    """
    Returns a GeoDataFrame with the 1D calculation points
    """

    ds = Dataset(fn_fou)
    network_node_id = ds.variables['mesh1d_node_id']
    network_node_id_list = []
    for i in range(len(network_node_id)):
        network_node_id_list.append(array_to_str(network_node_id[i, :].data))

    x_list = list(ds.variables['mesh1d_node_x'][:].data)
    y_list = list(ds.variables['mesh1d_node_y'][:].data)

    df_network = pd.DataFrame({'x': x_list, 'y': y_list}, index=network_node_id_list)
    gdf_network = gpd.GeoDataFrame(df_network, geometry=gpd.points_from_xy(df_network.x, df_network.y), crs=ds.variables['projected_coordinate_system'].epsg)

    return gdf_network

def get_nodes(fn_fou):
    """
    Returns a GeoDataFrame with the nodes (start/end of branches, not calculation points)
    """

    ds = Dataset(fn_fou)
    network_node_id = ds.variables['Network_node_id']
    network_node_id_list = []
    for i in range(len(network_node_id)):
        network_node_id_list.append(array_to_str(network_node_id[i, :].data))

    x_list = list(ds.variables['Network_node_x'][:].data)
    y_list = list(ds.variables['Network_node_y'][:].data)

    df_network = pd.DataFrame({'x': x_list, 'y': y_list}, index=network_node_id_list)
    gdf_network = gpd.GeoDataFrame(df_network, geometry=gpd.points_from_xy(df_network.x, df_network.y), crs=ds.variables['projected_coordinate_system'].epsg)

    return gdf_network

def get_boundary_nodes(fn_bc, fn_fou):
    """
    Returns a GeoDataframe of node id's from the 1d boundary condition file
    """

    bc_node_list = []
    with open(fn_bc, 'r') as file:
        lines = file.readlines()

        current_quantity = None
        current_name = None

        for line in lines:
            line = line.strip()
            if line.startswith('quantity'):
                current_quantity = line.split('=')[1].strip()
            elif line.startswith('name'):
                current_name = line.split('=')[1].strip()
            elif line == '' and current_quantity in ['waterlevelbnd', 'discharge']:
                # Add the name to the list if the quantity matches the specified values
                if current_name is not None:
                    bc_node_list.append(current_name)
                # Reset the variables for the next section
                current_quantity = None
                current_name = None

    gdf_nodes = get_nodes(fn_fou)

    return gdf_nodes[gdf_nodes.index.isin(bc_node_list)]

def remove_boundary_nodes(gdf_calcpoints, gdf_boundary_nodes):
    """
    Returns a GeoDataFrame with all entries removed where the index in a list of boundary node id's.
    """
    return gdf_calcpoints[~gdf_calcpoints.geometry.apply(lambda x: any(gdf_boundary_nodes.geometry.intersects(x)))]



if __name__ == '__main__':
    fn_fou = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\input\model\Output\001\dflowfm\output\FlowFM_fou.nc'
    fn_bc = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\input\model\Output\001\dflowfm\FlowFM_boundaryconditions1d.bc'

    bc_node_list = get_boundary_nodes(fn_bc, fn_fou)
    gdf_nodes = get_nodes(fn_fou)
    gdf_calcpoints = get_calculation_points(fn_fou)
    gdf_boundary_nodes = get_boundary_nodes(fn_bc, fn_fou)
    gdf_calcpoints_without_boundary = remove_boundary_nodes(gdf_calcpoints, gdf_boundary_nodes)

    print('Bye!')