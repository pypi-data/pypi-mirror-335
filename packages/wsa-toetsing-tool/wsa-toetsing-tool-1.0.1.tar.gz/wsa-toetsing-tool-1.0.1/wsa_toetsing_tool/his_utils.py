import wsa_toetsing_tool.hkvsobekpy_wsa as hkv
import pandas as pd
import numpy as np


def his_to_df(his_file, calcpnt_par_statistiek):
    """
    Load sobek his files into a dataframe
    his_file datatype: 
    - string 
    - list of strings. Each his file must have the same length and index with subsequent timeframes
    """
    his_df_tmp = []
    if type(his_file) == list:
        for l in his_file:
            his_df_tmp.append(hkv.read_his.ReadMetadata(l).DataFrame())
        his_df = pd.concat(his_df_tmp).sort_index()
    else:
        his_df = hkv.read_his.ReadMetadata(his_file).DataFrame()
    his_df.columns.names = ["parameters", "locations"]

    # Check of the opgegeven parameter voorkomt in de his_df
    if calcpnt_par_statistiek not in list(his_df.columns.unique(0)):
        raise ValueError(
            f"{calcpnt_par_statistiek} komt niet voor in de calcpnt.his kolommen {str(list(his_df.columns.unique(0)))}. Verbeter de input variabele 'calcpnt_par_statistiek'.")

    his_df = his_df.xs(calcpnt_par_statistiek, level=0,
                       axis=1, drop_level=False)
    his_df.columns = his_df.columns.remove_unused_levels()
    return his_df.sort_index()


def filter_df_by_network(his_df, network_gdf):
    """
    Filter his_dataframe voor netwerklocaties
    """
    mask_locations_in_network = his_df.columns.levels[1].isin(
        network_gdf.index.values)
    dropped_calculation_points = his_df.columns.levels[1][np.invert(
        mask_locations_in_network)]
    print(
        f"De calculation point data die niet in het network voorkomt wordt verwijderd: {dropped_calculation_points}")

    return his_df.loc[:, (slice(None), his_df.columns.levels[1][mask_locations_in_network])]


def exclude_nodes_from_network(exclude_id: list, network):
    mask = network.index.isin(exclude_id)
    print(
        f"Nodes {network[mask].index.to_list()} op basis van gebruiker input verwijderd uit netwerk")
    return network[~mask]