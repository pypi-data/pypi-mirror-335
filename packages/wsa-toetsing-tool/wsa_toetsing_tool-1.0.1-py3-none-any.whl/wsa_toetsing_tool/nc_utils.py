from netCDF4 import Dataset
import numpy as np
import pandas as pd
from datetime import datetime


def array_to_str(ar):
    '''

    Args:
        ar: array

    Returns: string

    '''
    return "".join(str(s, encoding="UTF-8") for s in ar)

def get_node_list(nc, var_node_id):
    """Get list of the node names/ids from the name/id variabele. The input variable ends with _name or _id"""
    nodes = nc.variables[var_node_id]
    node_list = []
    for i in range(len(nodes)):
        node_list.append(array_to_str(nodes[i, :].data))
    return node_list

def get_timeseries(nchis):
    """Get timesteps from hisfile."""
    time = nchis.variables["time"][:].data
    start = nchis.variables["time"].units
    startdate = start[14:33]
    sd = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
    time = pd.to_timedelta(time, unit="s") + sd
    return time

def nc_reader(pad_nc_file: str, list_variables: list):
    """
    pad_nc_file: path of the nc file with results
    list_variables: a list with the variables for which results will be extracted, first entry has to contain the
    column with the id
    """
    nchis = Dataset(pad_nc_file, mode="r")
    time = get_timeseries(nchis)

    x = nchis.variables[list_variables[1]][:].data[0]
    sequence = np.arange(1, len(x) + 1, 1)

    if list_variables[0] == "No id":
        id_object = sequence
    else:
        id_object = get_node_list(nchis, list_variables[0])
        id_object = [item.rstrip() for item in id_object]

    ids_list = []
    for i in id_object:
        for j in range(len(time)):
            ids_list.append(i)

    seq_list = []
    for i in sequence:
        for j in range(len(time)):
            seq_list.append(i)

    time_list = []
    for j in range(len(id_object)):
        for i in time:
            time_list.append(i)

    tuples = list(zip(ids_list, time_list))
    index = pd.MultiIndex.from_tuples(tuples, names=["id", "time"])

    d_results = {}
    for i in list_variables[1:]:
        data_variable = nchis.variables[i][:].data
        data_variable = data_variable.flatten(order="F").tolist()
        d_results[i] = data_variable
    d_results["sequence"] = seq_list

    df = pd.DataFrame(data=d_results, index=index)

    return df

if __name__ == "__main__":
    # This code is run when you run this file separately
    mapnc = r"D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\input\dhydro\DFM_map.nc"
    founc = r"D:\Downloads\hydrologic_reeksberekeningscripts-en-voorbeeldmappenstructuur_2024-10-25_1415\Winter_base\dflowfm\output\DFM_fou.nc"
    #df = nc_reader(pad_nc_file=mapnc, list_variables=['mesh1d_node_id', 'mesh1d_s1'])
    fou_df = nc_reader(pad_nc_file=founc, list_variables=[])

    print("Done!")