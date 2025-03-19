import re
import geopandas as gpd
import pandas as pd
import os

from wsa_toetsing_tool.config import (NTW_VERSION_SUPPORT, CRS_28992,
                                 COLS_NTW, COLS_ND_FROM, COLS_ND_TO, COLS_ND, COL_INDEX_NODE, )
from wsa_toetsing_tool.helpers import point, fn_correct_capitals


class Network(gpd.GeoDataFrame):
    r"""
    Sobek 2 `Network` object, which can read and view a network file.
    The `Network` object can be instantiated by directing to the file location::
        network_n = Network.read_network_n(r'SBK_VB.lit\10\NETWORK.NTW')
    """

    _metadata = ['file_ntw', 'file_ntwwq', 'crs']
    ntw = None

    @property
    def _constructor(self):
        return Network

    def __init__(self, *args, **kwargs):
        if "file_ntw" in kwargs.keys():
            Network.file_ntw = kwargs["file_ntw"]

        kwargs.pop("file_ntw", None)
        super(Network, self).__init__(*args, **kwargs)

    @staticmethod
    def _verify_version(file_ntw: str):
        """Verify supported versions for NTW."""
        with open(file_ntw) as f:
            ln = f.readline()
            if not any(re.search(r"\d\.\d", ln).group() in s for s in NTW_VERSION_SUPPORT):
                raise Exception(
                    "Version Network.NTW too old (only v6.6 is supported)")
        return

    @staticmethod
    def _nbranch(file_ntw: str) -> int:
        """Get linenumber where to read NTW."""
        with open(file_ntw) as f:
            lines = f.readlines()
            for nline, ln in zip(range(len(lines)), lines):
                if ln.strip() == '"*"':
                    return nline - 1

    @staticmethod
    def _to_individual_nodes(df: pd.DataFrame):
        """Combine individual from and to nodes to a single dataframe."""
        df_nodes_from = (df.loc[:, COLS_ND_FROM]
                         .rename(columns={key: value for key, value in zip(COLS_ND_FROM, COLS_ND)})
                         .set_index(COL_INDEX_NODE))
        df_nodes_to = (df.loc[:, COLS_ND_TO]
                       .rename(columns={key: value for key, value in zip(COLS_ND_TO, COLS_ND)})
                       .set_index(COL_INDEX_NODE))
        return (pd.concat([df_nodes_from, df_nodes_to])
                .drop_duplicates()
                .assign(geometry=lambda x: point(x)))

    @classmethod
    def read_network_n(cls, file_ntw: str = None, crs=CRS_28992, **kwargs) -> 'Network':
        """
        Read sobek channel.
        TODO: How to link it to sample elevation (in Case??).
        """

        file_ntw = fn_correct_capitals(file_ntw)

        cls._verify_version(file_ntw)
        nbranch = cls._nbranch(file_ntw)
        df = (pd
              .read_csv(file_ntw, skiprows=[0], header=None, nrows=nbranch, names=list(COLS_NTW.keys()), dtype=COLS_NTW)
              .pipe(cls._to_individual_nodes))
        sbk_chan_n = gpd.GeoDataFrame(
            df, geometry=df["geometry"], crs=crs, **kwargs)

        return Network(sbk_chan_n, crs=crs, file_ntw=file_ntw)


# if __name__ == '__main__':
   # folder = r'c:\Users\907109\Box\BH9135 HHD DDWoW Team\BH9135 Technical Data\Automatiseren WSA\Voorbeeld bestanden'
   # ntw = os.path.join(folder, 'Vlietp.lit', '1', 'NETWORK.NTW')
    #network = Network.read_network_n(ntw)
    # print(network.head())
