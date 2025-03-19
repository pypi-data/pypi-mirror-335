import os

import numpy.linalg
import pandas as pd
import geopandas as gpd
import numpy as np
import rasterio
import logging
import xarray as xr
from tqdm import tqdm
from rasterstats import zonal_stats
from pathlib import Path

from wsa_toetsing_tool.helpers import (set_crs, validate_crs, validate_columns_in_shp,
                                                    validate_raster_input, validate_overlap_KAE_PG,
                                                    clip_raster_to_shape, create_dir, validate_input,
                                                    bgt_functie_to_rst, gdf_to_raster, mosaic_raster,
                                                    export_max_wl_to_csv)
from wsa_toetsing_tool.toetsing import toetsinganalyse, tabel_toetsingsanalyse
from wsa_toetsing_tool.sobek_netwerk import Network
from wsa_toetsing_tool.his_utils import filter_df_by_network, his_to_df, exclude_nodes_from_network
from wsa_toetsing_tool.dhydro_utils import fou_series_to_gdf, get_boundary_nodes, remove_boundary_nodes
from wsa_toetsing_tool.knelpunten import maak_knelpunten_shape, waterdiepte_filter_norm, \
    statistiek_per_gebied, genereer_waterdiepte_raster, genereer_verschil_raster, waterstandstatistiek, \
    _mask_inundatie_raakt_watervlak
from wsa_toetsing_tool.config import COL_LIST, FN_WATSTAT, FN_PREFIX_WATERDIEPTE, FN_PREFIX_WATERSTAND, \
    COL_NODE_TYPE, COL_PEIL, BGT_PANDEN_RST, BGT_WATERVLAKKEN_RST, FOLDER_KNELPUNTEN, FOLDER_TOETSING, \
    FOLDER_BEWERKTE_INPUT, T_LIST_DICT, INTERPOLATE_RETURN_PERIODS

class Knelpunten():
    def __init__(self, fn_afwateringsgebieden: str, fn_hoogtegrid: str, output_dir: str,
                 output_prefix: str = "", klimaatscenario="", wsa_titel=""):
        """Class voor het afleiden van de knelpunten in de watersysteemanalyse (WSA). 

        Args:
            fn_afwateringsgebieden (str): bestandslocatie polygonen van afwaterings- of peilgebieden (shp of gpkg)
            fn_hoogtegrid (str): bestandslocatie raster met ahn (.tif)
            output_dir (str): bestandslocatie (directorie) voor wegschrijven output
            output_prefix (str, optional): optioneel, prefix voor output bestanden. Defaults to "".
            klimaatscenario (str): optioneel, naam het van klimaatscenario. Wordt toegevoegd aan de naam van de knelpuntenfolder en ingevoerd in de knelpuntenshape
        """

        validate_input([fn_afwateringsgebieden, fn_hoogtegrid])
        validate_crs(fn_afwateringsgebieden)

        if len(klimaatscenario) > 0:
            knelpunten_pf = "_"+klimaatscenario
        else:
            knelpunten_pf = ""

        # Create paths
        self.path_output = create_dir(
            os.path.join(output_dir, FOLDER_KNELPUNTEN+knelpunten_pf))
        self.path_tussenresultaat = create_dir(
            os.path.join(output_dir, FOLDER_BEWERKTE_INPUT))
        # self.fn_log = os.path.join(output_dir, datetime.today().strftime("%Y%m%d_%H%M") + '.log')

        self.fn_gebieden = fn_afwateringsgebieden

        # Clip AHN to boundary shape
        self.fn_hoogtegrid = clip_raster_to_shape(
            fn_hoogtegrid, fn_afwateringsgebieden, export_folder=self.path_tussenresultaat)
        self.fn_calcpnt_his = None
        self.fn_network = None
        self.output_prefix = output_prefix
        self.period_growingseason = None
        self.calcpnt_par_statistiek = None

        self._waterstandsstatistiek = None
        self._waterstand_cols = COL_LIST
        self.ntw_nodes = None

        self.waterstand_grid = None
        self.waterdiepte_grid = None
        self._fn_waterstand_grid = None
        self._fn_waterdiepte_grid = None
        self._fn_waterdiepte_crop = None
        #self._fn_waterdiepte_filter_norm = None
        self._fn_waterdiepte_norm = None

        self._fn_knelpunten_shp = None
        self._fn_gebieden_watstat = None
        self._fn_overstromingsvlak_gebieden = None
        self._fn_bgt_rst_water = None

        self.norm_shape = None
        self.knelpunten = None
        self.gebieden_watstat = None
        self.transform = None
        self.profile = None
        self._gebieden = None
        self._netwerk = None
        self._sortering_events = None

        self.klimaat_scenario = klimaatscenario
        self.wsa_titel = wsa_titel

    @property
    def gebieden(self):
        """
        Returns:
            geodataframe: Shape met ingelezen peil/afwateringsgebieden
        """
        if self._gebieden is None:
            self._gebieden = self._read_afwateringsgebieden()
        return self._gebieden

    def importeer_waterstandsstatistiek(self,
                                        fn_stats: str,
                                        stat_dict: dict = None,
                                        index_col: str = 'index'):
        """
            Laadt een shapefile of geopackage en gebruik attribuut-data als waterstandsstatistiek
            Args:
                fn_stats: bestandslocatie van GIS-bestand met waterstandsstatistiek
                stat_dict: dictionary met mapping van kolomnamen. De keys van de dictionary zijn de kolomnamen in het
                GIS-bestand. De values van de dict zijn de bijbehorende beschermingsniveaus, te kiezen uit:
                    ['T10','T10_GROEI','T25','T50','T100']
                index_col: String met de kolomnaam die als index geldt
        """
        gdf_stat = gpd.read_file(fn_stats)
        gdf_stat = gdf_stat.set_index(index_col)
        if stat_dict:
            gdf_stat = gdf_stat.rename(stat_dict)
            stat_cols = list(stat_dict.values()) + ['geometry']
            gdf_stat = gdf_stat[stat_cols]

        self._waterstandsstatistiek = gdf_stat

        output_filename = os.path.join(self.path_output, f'statistiek/{self.output_prefix}{FN_WATSTAT}_{self.klimaat_scenario}.shp')
        Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
        self._waterstandsstatistiek.to_file(output_filename)


        return self._waterstandsstatistiek
    def genereer_waterstandsstatistiek(self,
                                       result_settings: dict,
                                       period_growingseason: list = [(3, 1), (10, 1)],
                                       afweenheid_col_code='AFWEENHEID',
                                       venster_array=[0, 10],
                                       Ggi=0.44,
                                       GgN=0.12,
                                       TOI=10,
                                       plots=True,
                                       exclude_id=None,
                                       drop_rows_with_nodata=False,
                                       n_jaren_plotposities=None
                                       ):
        """Genereer gumbel waterstandsstatistiek voor het opgegeven his bestand, geaggreerd naar de gebieden shape
        Args:
            result_settings (dict): Dictionary met settings betreffende de sobek/dhydro resultaten.
            period_growingseason (list, optional): format: [(mm, dd), (mm, dd)] - periode voor filtering groeiseizoen. Defaults to [ (3, 1), (10, 1)].
            afweenheid_col_code (str, optional): kolomnaam in de gebieden shape met de afwateringseenheid. Defaults to 'AFWEENHEID'.
            venster_array (list, optional): het venster welke gebruikt wordt als filter om de gebeurtenissen mee te
                nemen voor de bepaling van de Gumbel fit. Het venster is een array van 
                twee waarden, vaak wordt [0,10] gekozen, waar 0 overeenkomt met de meest 
                extreme waarde en 10 de op 10 na meest extreme waarde. In ander woorden, 
                in dit geval is het venster de 10 meest extreme waarden.. Defaults to [0, 10].
            Ggi (float, optional): Gringgorten plotposities i . Defaults to 0.44.
            GgN (float, optional):  Gringgorten plotposities N. Defaults to 0.12.
            TOI (int, optional):   Waarde met de terugkeertijd of interest voor het bepalen van het gewogen 
                gemiddelde. Dit wordt gebruikt voor een terugkeertijd welke tenminste 2 
                gebeurtenissen en 2 gebeurtenissen na zicht heeft. Gewoonlijk kan dit 
                gebruikt worden voor het bepalen van de T10, welke soms nog in de 
                'knik' ligt.. Defaults to 10.
            plots (bool, optional): Export Gumbel plots (heeft veel invloed op de performance). Defaults to True.
            exclude_id (list, optional):
            drop_rows_with_nodata (bool, optional): Verwijder objecten waar geen waterstandsstatistiek voor is afgeleid uit de tabel, default False 
            n_jaren_plotposities (int, optional): Definieer het aantal gumbel plotposities (aantal jaren waarvoor de reeks representatief is). Als hier geen aantal is opgegeven wordt dit aantal automatisch afgeleid van de tijdreeks. Default is None

        Returns:
            geodataframe: waterstandssatistiek per rekenpunt
        """

        print("Het maken van figuren vertraagd de performance aanzienlijk. Zet deze optie uit met `plots=False`") if plots else None

        print(
            f'Waterstandsanalyse wordt uigevoerd op basis van opgegeven network nodes: {str(self.ntw_nodes)}')

        print(
            f'Start afleiden waterstandsstatistiek uit {self.fn_calcpnt_his}')

        self.period_growingseason = period_growingseason
        sortering_df = None
        max_wl_df = None

        if result_settings['modelpakket'] == 'sobek':
            self.calcpnt_par_statistiek = result_settings['calcpnt_par_statistiek']
            self._netwerk = self._read_network(result_settings)
            # Logic to read Sobek results from HIS file
            max_wl_df = his_to_df(result_settings['fn_calcpnt_his'], result_settings['calcpnt_par_statistiek'])
            self._netwerk = self._netwerk[self._netwerk.loc[:, "ObjID"].isin(
                result_settings['ntw_nodes'])]

            if exclude_id is not None:
                self._netwerk = exclude_nodes_from_network(exclude_id, self._netwerk)

            max_wl_df = filter_df_by_network(max_wl_df, self._netwerk)
            sortering_df = max_wl_df

        elif result_settings['modelpakket'] == 'dhydro':
            # Add logic to read dhydro model result from Fou file
            max_wl_df, self._netwerk = fou_series_to_gdf(result_settings['dhydro_result_folder'],
                                               result_settings['max_wl_var'],
                                               result_settings['max_wl_time_var'])
            self.calcpnt_par_statistiek = result_settings['max_wl_var']

            if result_settings['exclude_boundary_nodes']:
                fn_bc = result_settings['boundary_conditions_file']

                source_dir = Path(result_settings['dhydro_result_folder'])
                # Retrieve first fou.nc file to extract nodes (instead of calculation points)
                try:
                    fn_fou = source_dir.rglob("*_fou.nc").__next__()
                except StopIteration:
                    logging.ERROR("No fou.nc file found in the specified directory")
                boundary_nodes = get_boundary_nodes(fn_bc, fn_fou)
                self._netwerk = remove_boundary_nodes(self._netwerk, boundary_nodes)

            if exclude_id is not None:
                self._netwerk = exclude_nodes_from_network(exclude_id, self._netwerk)



            max_wl_df = filter_df_by_network(max_wl_df, self._netwerk)

            # Bepaal nogmaals de maximale waterstanden maar nu met tijdstip van het begin van de simulatie in plaats van
            # het tijdstip van optreden
            sortering_df, _ = fou_series_to_gdf(result_settings['dhydro_result_folder'],
                                               result_settings['max_wl_var'])





        self._sortering_events = self.sorteer_events_per_afwateringseenheid(sortering_df,
                                                                            afweenheid_col_code,
                                                                            self._netwerk,
                                                                            afwateringsgebieden=self.gebieden)

        # genereer waterstandsstatistiek
        self._waterstandsstatistiek = waterstandstatistiek(max_wl_df=max_wl_df, network=self._netwerk,
                                                           period_growingseason=self.period_growingseason,
                                                           par=self.calcpnt_par_statistiek, venster_array=venster_array,
                                                           Ggi=Ggi, GgN=GgN, TOI=TOI,
                                                           export_folder_plot=self.path_output, plots=plots,
                                                           n_jaren_plotposities=n_jaren_plotposities,
                                                           modelpakket=result_settings['modelpakket'])

        output_filename = os.path.join(self.path_output,
                                       f'statistiek/{self.output_prefix}{FN_WATSTAT}_{self.klimaat_scenario}.shp')
        Path(output_filename).parent.mkdir(parents=True, exist_ok=True)
        self._waterstandsstatistiek.to_file(output_filename)

        print(f'Waterstandstatistieken weggeschreven in {self.path_output}')

        sortering_df.to_csv(os.path.join(self.path_output,
                                         f'statistiek/{self.output_prefix}max_wl_{self.klimaat_scenario}.csv'))
        print(f'Maximale waterstand per simulatie weggeschreven in {self.path_output}')


        print(
            f"Objecten met nodata: {self._waterstandsstatistiek.loc[self._waterstandsstatistiek.isna().any(axis=1)].index.to_list()}")
        if drop_rows_with_nodata:
            self._waterstandsstatistiek = self._waterstandsstatistiek.dropna()
            fn_export_verwijderde_objecten = os.path.join(
                self.path_tussenresultaat, "objecten waterstandsstatistiek verwijderd.csv")
            self._waterstandsstatistiek.loc[self._waterstandsstatistiek.isna().any(
                axis=1)].to_csv(fn_export_verwijderde_objecten)
            print(
                f"Objecten met nodata values verwijderd en weggeschreven naar: {fn_export_verwijderde_objecten}")

        return self._waterstandsstatistiek

    @property
    def waterstandsstatistiek(self):
        """
        Returns:
            geodateframe: afgeleide waterstandsstatistiek. Warning als de waterstandsstatistiek nog niet is gegenereerd (.genereer_waterstandsstatistiek)
        """
        if self._waterstandsstatistiek is None:
            raise Warning(
                "Waterstandsstatistiek niet ingeladen. Genereer nieuwe waterstandsstatistiek of lees bestaande waterstandsstatistiek in.")
        return self._waterstandsstatistiek


    def genereer_herhalingstijd_raster(self, fn_herhalingstijd):
        """Genereer raster met herhalingstijd per pixel
                Args:
                    fn_herhalingstijd (String): Bestandsnaam waar het raster weg te schrijven

                Returns:
                    None
                """

        def calculate_loglin_parameters(row):
            """
            Calculates the slope and intercept parameters using the log of return periods
            """
            log_return_periods = np.log(list(INTERPOLATE_RETURN_PERIODS.values()))
            water_levels = row[list(INTERPOLATE_RETURN_PERIODS.keys())].values.astype(float)
            try:
                coefficients = np.polyfit(log_return_periods, water_levels, 1)
                return coefficients
            except np.linalg.LinAlgError:
                print(f"Kan geen logaritmische regressie uitvoeren op afwateringsgebied, mogelijk geen rekenpunt binnen afwateringsgebied:\n {row}")


        # Calculate parameters
        self.peil_per_gebied[['slope','intercept']] = self.peil_per_gebied.apply(lambda row: pd.Series(calculate_loglin_parameters(row)), axis=1)

        # Determine temporary filenames
        fn_slope = os.path.join(self.path_output, f"temp/{self.output_prefix}herhalingstijd_inundatie_slope_{self.klimaat_scenario}.tif")
        fn_intercept = os.path.join(self.path_output, f"temp/{self.output_prefix}herhalingstijd_inundatie_intercept_{self.klimaat_scenario}.tif")

        # Export slope and intercept parameters to temp rasters
        gdf_to_raster(self.peil_per_gebied,'slope',rst_reference=self.fn_hoogtegrid,filename_output=fn_slope)
        gdf_to_raster(self.peil_per_gebied,'intercept',rst_reference=self.fn_hoogtegrid,filename_output=fn_intercept)

        # Read temp rasters
        with rasterio.open(self.fn_hoogtegrid) as src:
            elevation = src.read(1)
            elevation[elevation == src.nodata] = np.nan
            out_profile = src.profile

        with rasterio.open(fn_slope) as src:
            slope = src.read(1)
            slope[slope == src.nodata] = np.nan

        with rasterio.open(fn_intercept) as src:
            intercept = src.read(1)
            intercept[intercept == src.nodata] = np.nan

        # calculate return period
        t_log = (elevation - intercept) / slope
        t_log_clipped = np.clip(t_log, -700, 700)

        def safe_exp(x):
            try:
                return np.exp(x)
            except OverflowError:
                return np.inf

        return_period = safe_exp(t_log_clipped)

        with rasterio.open(fn_herhalingstijd, "w", **out_profile) as dest:
            dest.write_band(1, return_period)


    def sorteer_events_per_afwateringseenheid(self, his_df, afweenheid_col_code, netwerk, afwateringsgebieden):
        """
        Args:
            his_df (DataFrame): dataframe van het his-bestand
            netwerk (GeoDataFrame): Netwerk GeoDataFrame met puntlocaties van rekenpunten
            afwateringsgebieden (GeoDataFrame): Afwateringsgebieden voor de bepaling van een mediane maximale waterstand
            per afwateringsgebied per event

        Returns:
            geodataframe: sortering van datums van hoogste waterstand per kleinste afwateringseenheid.

        """

        his_df_t = his_df.T.copy()
        his_df_t.index = his_df_t.index.droplevel(0)

        gdf = gpd.GeoDataFrame(his_df_t.join(netwerk['geometry'], how='inner'), geometry='geometry', crs=self._netwerk.crs)
        gdf = gdf.sjoin(afwateringsgebieden[[afweenheid_col_code, 'geometry']]
                        .set_index(afweenheid_col_code), how='left', predicate='intersects')\
            .rename(mapper={'index_right': afweenheid_col_code}, axis=1)

        df = gdf.groupby(afweenheid_col_code).median(numeric_only=True)

        result_df = pd.DataFrame(index=range(1, len(df.columns) + 1), columns=df.index)

        # Iterate over each row in the transposed dataframe
        for idx, row in df.iterrows():
            # Sort the row by values in descending order
            sorted_row = row.sort_values(ascending=False)
            # Get the datetime notations (column names) in the sorted order
            sorted_dates = sorted_row.index
            # Assign the sorted datetime notations to the result dataframe
            result_df.loc[:, idx] = sorted_dates.values

        return result_df

    def exporteer_sortering_events(self, fn_sortering_events):
        if self._sortering_events is not None:
            self._sortering_events.to_excel(fn_sortering_events)
        else:
            print("Geen sortering van events is beschikbaar")


    def genereer_peil_per_gebied(self, par="mean", additional_pars=['min','mean','median','max']):
        """
        Aggregeer waterstandsstatiekpunten naar de opgegeven afwatering/peilgebieden
        Args:
            par: opties voor aggregatie: mean, min, max, median
        Returns: geodataframe met geaggrereerde waterstandsstatistiek per vlak

        """
        print(
            f"Start aggregatie waterstandsstatiek naar vlakken; parameter {par}")
        self.gebieden_watstat = statistiek_per_gebied(
            self.gebieden, self.waterstandsstatistiek, par=par, additional_pars=additional_pars)
        self._fn_gebieden_watstat = os.path.join(
            self.path_output, f"statistiek/{self.output_prefix}gebieden_statistiek_{self.klimaat_scenario}.shp")

        Path(self._fn_gebieden_watstat).parent.mkdir(parents=True, exist_ok=True)
        self.gebieden_watstat.to_file(self._fn_gebieden_watstat)
        print(f'{self._fn_gebieden_watstat} aangemaakt')

        return self.gebieden_watstat

    @property
    def peil_per_gebied(self):
        if self.gebieden_watstat is None:
            raise Warning(
                "Shape niet ingeladen. Run de functie genereer_peil_per_gebied")
        return self.gebieden_watstat


    def genereer_waterstandsrasters(self, fn_peil_per_gebied=None, initieel_peil_kolom = None, fn_suffix=''):
        """
        Genereert waterstandsrasters op basis van een vlakkenshape. De kolomnamen in de shape zijn tenminste: ['T10', 'T10 GROEISEIZOEN', 'T25', 'T50', 'T100']
        Args:
            fn_peil_per_gebied: bestandslocatie geopackage met waterstandstatistiek geaggregeerd naar vlakken
            initieel_peil_kolom: Indien ingevuld zal ook het initiele peil om worden gezet in een waterstandsraster. Default None
            fn_suffix: suffix voor bestandsnaam

        Returns: dictionary met bestandslocatie rasters

        """
        print("Start genereren waterstandsrasters")
        if fn_peil_per_gebied is None:
            peil_per_gebied = self.peil_per_gebied
        else:
            validate_input([fn_peil_per_gebied])
            peil_per_gebied = gpd.read_file(fn_peil_per_gebied)

        self._fn_overstromingsvlak_gebieden = {}

        tx_list = COL_LIST.copy()
        if initieel_peil_kolom:
            peil_per_gebied['initieel'] = peil_per_gebied[initieel_peil_kolom].astype(np.float64)
            tx_list.insert(0, 'initieel')

        for Tx in tx_list:
            fn_tmp = os.path.join(
                self.path_output, f"waterstandrasters/{self.output_prefix}gebieden_waterstand_{Tx}{fn_suffix}.tif")
            gdf_to_raster(peil_per_gebied, Tx, self.fn_hoogtegrid, fn_tmp)
            self._fn_overstromingsvlak_gebieden[Tx] = fn_tmp
            print(
                f"Waterstandsgrid {Tx} gegenereerd: {self._fn_overstromingsvlak_gebieden[Tx]}")
        logging.info(f'{self._fn_overstromingsvlak_gebieden}')
        return self._fn_overstromingsvlak_gebieden

    def genereer_waterdiepterasters(self, fn_overstromingsvlak=None, drempel_diepte=0.01, fn_suffix=''):
        """
        Genereert waterdiepteraster op basis van de waterstandsrasters en de AHN
        Args:
            fn_overstromingsvlak: dictionary met waterstandsrasters. {"T10": "xxx.tif", "T10 GROEISEIZOEN": "xxx.tif", "T25": "xxx.tif", "T50": "xxx.tif", "T100": "xxx.tif"}
            drempel_diepte: minimale diepte voor wegschrijven. Alle waardes onder deze waarde worden als 0 weggeschreven.
            fn_suffix: suffix voor bestandsnaam
        Returns: dictionary met gegenereerde rasters

        """
        print("Start genereren waterdiepterasters")
        if fn_overstromingsvlak is None:
            fn_overstromingsvlak = self._fn_overstromingsvlak_gebieden
            validate_input([fn_overstromingsvlak])

        self._fn_waterdiepte_gebieden = {}
        for Tx in fn_overstromingsvlak.keys():
            fn_tmp = os.path.join(
                self.path_output, f"waterdiepterasters/{self.output_prefix}gebieden_waterdiepte_{Tx}{fn_suffix}.tif")
            self._fn_waterdiepte_gebieden[Tx] = genereer_waterdiepte_raster(fn_overstromingsvlak[Tx],
                                                                            self.fn_hoogtegrid, fn_tmp, drempel_diepte)
            print(
                f"Waterdieptegrid {Tx} gegenereerd: {self._fn_waterdiepte_gebieden[Tx]}")
        logging.info(f'{self._fn_waterdiepte_gebieden}')
        return self._fn_waterdiepte_gebieden

    def genereer_verschilrasters(self, fn_invoerrasters, referentie, ref_suffix='referentie', nodata_to_zero=True,
                                 ignore_negative=True):
        """
        Vergelijk alle rasters in fn_invoerrasters met een referentieraster. Nodata in rasters wordt 0 beschouwd.
        Een negatieve uitkomst wordt op 0 gezet.

        :param fn_invoerrasters: dict met rasternaam en bestandslocatie
        :param referentie: rasternaam die als referentie gebruikt wordt
        :param ref_suffix: achtervoegsel voor de referentierasters
        :param nodata_to_zero: Indien True, zet de functie alle nodata-waardes in het raster om in 0
        :param ignore_negative: Indien True worden alle negatieve waardes omgezet in 0 waardes.
        :return: Bestandsnamen van weggeschreven verschilrasters
        """
        self._fn_waterdiepte_gebieden_verschil = {}

        if isinstance(referentie, str):
            # Compare all rasters with a single raster
            if referentie in fn_invoerrasters.keys():

                # Iterate over water depth rasters
                for Tx in fn_invoerrasters.keys():
                    if Tx == referentie:
                        continue

                    fn_tmp = os.path.join(
                        self.path_output, f"waterdiepte_verschilrasters/{self.output_prefix}gebieden_waterdiepte_verschil_{Tx}-{ref_suffix}.tif")
                    self._fn_waterdiepte_gebieden_verschil[Tx] = genereer_verschil_raster(fn_invoerrasters[Tx],
                                                                                          fn_invoerrasters[referentie],
                                                                                          fn_tmp,
                                                                                          nodata_to_zero,
                                                                                          ignore_negative
                                                                                          )
                    print(
                        f"Waterdiepteverschil {Tx} gegenereerd: {self._fn_waterdiepte_gebieden_verschil[Tx]}")

                logging.info(f'{self._fn_waterdiepte_gebieden_verschil}')
                return self._fn_waterdiepte_gebieden_verschil
            else:
                raise NameError(
                    f"Raster '{referentie}' doet not exist. The available rasters are: {list(fn_invoerrasters.keys())}")

        elif isinstance(referentie, dict):
            # Compare two sets of rasters, are compared on key
            # Check if both contain the same keys
            for Tx in fn_invoerrasters.keys():
                if Tx in referentie.keys():
                    fn_tmp = os.path.join(
                        self.path_output,
                        f"waterdiepte_verschilrasters/{self.output_prefix}gebieden_waterdiepte_verschil_{Tx}-{ref_suffix}.tif")
                    self._fn_waterdiepte_gebieden_verschil[Tx] = genereer_verschil_raster(fn_invoerrasters[Tx],
                                                                                          referentie[Tx],
                                                                                          fn_tmp,
                                                                                          nodata_to_zero,
                                                                                          ignore_negative)
                    print(
                        f"Waterdiepteverschil {Tx} gegenereerd: {self._fn_waterdiepte_gebieden_verschil[Tx]}")

            logging.info(f'{self._fn_waterdiepte_gebieden_verschil}')
            return self._fn_waterdiepte_gebieden_verschil



        else:
            raise NotImplementedError


    def bepaal_toename_volume(self, fn_waterdiepteverschilrasters, fn_gebieden, code_column='CODE',
                              output_filename='Toename_volume'):
        """
        Bepaal het volumetoename aan de hand van de waterdiepteverschilrasters.
        Per peilgebied worden de pixels bij elkaar opgeteld en vermenigvuldigt met het oppervlak van de pixel.

        :param fn_waterdiepteverschilrasters: Dictionary met herhalingstijden en bijbehorende rasterlocaties
        :param fn_gebieden: Bestandsnaam van de peilgebieden shapefile
        :param code_column: Naam van de kolom waar de peilgebiedcode in opgeslagen is. Default: 'CODE'
        :param output_filename: Bestandsnaam voor het wegschrijven. Wordt voorafgegaan door de prefix.
        :return: None
        """

        print("Start bepalen volumetoename per herhalingstijd")
        validate_crs(fn_gebieden)
        gebieden = gpd.read_file(fn_gebieden)
        gebieden = gebieden.to_crs("EPSG:28992")
        gdf = gebieden[[code_column, 'geometry']].copy(deep=True)

        for Tx in fn_waterdiepteverschilrasters.keys():
            # Read raster resolution
            src = rasterio.open(fn_waterdiepteverschilrasters[Tx])
            pixel_area = src.res[0] * src.res[1]

            gdf[Tx] = pd.DataFrame(
                zonal_stats(
                    vectors=gebieden['geometry'],
                    raster=fn_waterdiepteverschilrasters[Tx],
                    stats='sum'
                )
            )['sum'] * pixel_area

            # round to int, no float precision is needed
            gdf = gdf.fillna(-999)
            gdf[Tx] = gdf[Tx].astype(int)
            print(f"Volumetoename per gebied {Tx} bepaald.")

        fn_volumetoename_shp = os.path.join(
            self.path_output, f"volumetoename/{self.output_prefix}{output_filename}_{self.klimaat_scenario}.shp")

        fn_volumetoename_xlsx = os.path.join(
            self.path_output, f"volumetoename/{self.output_prefix}{output_filename}_{self.klimaat_scenario}.xlsx")

        gdf = gdf.round(decimals=0)

        Path(fn_volumetoename_shp).parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(fn_volumetoename_shp)
        gdf.drop(columns=['geometry']).set_index(code_column).to_excel(fn_volumetoename_xlsx)

    def genereer_knelpunten_shape(self, norm_raster, fn_diepte_grids, fn_peilgebieden, pg_code='CODE'):
        """
        Genereer knelpunten shapes op basis van het normen raster en de waterdiepte grids
        Args:
            norm_raster: normen raster met integer values 0, 10, 25, 50 en 100
            fn_diepte_grids: dictionary met waterdiepterasters. {"T10": "xxx.tif", "T10 GROEISEIZOEN": "xxx.tif", "T25": "xxx.tif", "T50": "xxx.tif", "T100": "xxx.tif"}
            fn_peilgebieden: bestandsnaam van peilgebiedenshape
            pg_code: kolomnaam met peilgebiedscodes
        Returns: bestandsfile knelpuntenshape

        """
        print("Start genereren knelpuntenshape")
        validate_input([fn_diepte_grids])
        norm_raster = validate_raster_input(
            norm_raster, self.fn_hoogtegrid, export_folder=self.path_tussenresultaat)
        # Maak temp folder
        path_temp = create_dir(os.path.join(self.path_output, "temp"))
        self._fn_waterdiepte_norm = waterdiepte_filter_norm(norm_raster, fn_diepte_grids, path_temp,
                                                      self.output_prefix)
        self._fn_knelpunten_shp = maak_knelpunten_shape(
            self._fn_waterdiepte_norm, fn_peilgebieden, norm_raster, self.path_output, self.output_prefix,
            self.wsa_titel, self.klimaat_scenario, pg_code=pg_code)

        # Verwijder temp folder
        #remove_folder_and_files(path_temp)
        print(f"Knelpuntenshape gegenereerd {self._fn_knelpunten_shp}")
        return self._fn_knelpunten_shp, self._fn_waterdiepte_norm

    def genereren_watervlakken_mask(self, bgt_shp: str, bgt_col_functie: str = "FUNCTIE", bgt_functie_watervlak: list = ["waterloop", "watervlak"]):
        """
        Genereert bgt raster met panden
        Args:
            bgt_shp: Shape met de BGT
            bgt_col_functie: kolomnaam in de bgt shape met functies
            bgt_functie_watervlak: bgt functies die als watervlak worden meegenomen

        Returns: bestandslocatie nieuwe raster
        """
        if self.fn_hoogtegrid is None:
            raise ValueError(
                "Lees eerst het AHN in zodat dit raster op basis van de AHN uitgelijnd kan worden.")

        fn_bgt = os.path.join(
            self.path_tussenresultaat, self.output_prefix+BGT_WATERVLAKKEN_RST)
        if os.path.exists(fn_bgt):
            self.watervlakken_mask = validate_raster_input(
                fn_bgt, self.fn_hoogtegrid, export_folder=self.path_tussenresultaat)
        else:
            validate_columns_in_shp(bgt_shp, [bgt_col_functie])
            self.watervlakken_mask = bgt_functie_to_rst(
                bgt_shp, filename_output=fn_bgt, reference_raster=self.fn_hoogtegrid, bgt_col_functie=bgt_col_functie,
                bgt_functie_objecttypen=bgt_functie_watervlak)
        return self.watervlakken_mask

    def filter_waterdiepteraster_raakt_watergang(self, bgt_rst, fn_waterdiepte=None):
        """
        Filter waterdiepterasters op het raakvlak met de watergang. Waarden die niet in directe verbinding staan met een watergang worden verwijderd.

        Args:
            bgt_rst: bgt raster met watervlakken
            fn_waterdiepte: dictinary met waterdiepte rasters

        Returns: dictionary met waterdiepterasters
        """
        print("Start filter waterdiepterasters op het raakvlak met de watergang")
        if fn_waterdiepte is None:
            fn_waterdiepte = self._fn_waterdiepte
        validate_input([bgt_rst, fn_waterdiepte])

        self._fn_waterdiepte_crop = {}

        for Tx, fn_waterdiepte_rst in fn_waterdiepte.items():
            logging.info(f'Bewerking raster {fn_waterdiepte_rst} gestart')
            mask_geom = _mask_inundatie_raakt_watervlak(
                fn_waterdiepte_rst, bgt_rst)
            with rasterio.open(fn_waterdiepte_rst) as src:
                out_image = src.read(1)
                out_profile = src.profile

            out_image = xr.where(mask_geom == True, out_image, np.nan)

            fn_out = fn_waterdiepte_rst.replace(
                '.tif', '_selectie-watergang.tif')
            with rasterio.open(fn_out, "w", **out_profile) as dest:
                dest.write_band(1, out_image)
            self._fn_waterdiepte_crop[Tx] = fn_out
            print(
                f"Gefilterd waterdiepteraster {Tx} gereed: {self._fn_waterdiepte_crop[Tx]}")
        return self._fn_waterdiepte_crop

    def lees_waterstandstatistiek(self, waterstandstatistiek_gpkg: str = None):
        """
        Als deze tool al eens (deels) is gerund, dan kan deze functie gebruikt worden om handmatig
        de waterstandstatistiek shapefile in te lezen. Gebruik hiervoor de GPKG, een SHP kort namelijk kolomnamen af.
        """
        if waterstandstatistiek_gpkg is None:
            waterstandstatistiek_gpkg = os.path.join(
                self.path_output, f'{FN_WATSTAT}_{self.klimaat_scenario}.shp')
        validate_input(waterstandstatistiek_gpkg)
        gdf = gpd.read_file(waterstandstatistiek_gpkg)
        if set(COL_LIST).issubset(gdf.columns):
            self._waterstandsstatistiek = gdf
            logging.info(
                f'Waterstatistiek resultaten ingelezen vanuit bestand: {waterstandstatistiek_gpkg}')
        else:
            raise ValueError(
                f'Shapefile bevat niet de juiste kolommen. Verwacht: {COL_LIST}, maar kreeg: {gdf.columns}')

    def lees_waterstand_grids(self, waterstand_grids: dict = None):
        """
        Als de tool al eens (deels) is gerund, dan kan deze functie gebruikt worden om handmatig de waterstand grids
        in te lezen (m NAP). Opbouw van de input dictionary is bijvoorbeeld:
        input = {'T10': 'padnaam/naar/Waterstand_T10.tif',
                 'T25': 'padnaam/naar/Waterstand_T25.tif',
                 etc.}
        De inputs worden 1 voor 1 ingelezen met rasterio en toegevoegd aan self.ws_grid
        """
        if waterstand_grids is not None:
            self._fn_waterstand_grid = waterstand_grids
        elif self._fn_waterstand_grid is None:
            self._fn_waterstand_grid = {}
            for Tx in COL_LIST:
                self._fn_waterstand_grid[Tx] = os.path.join(
                    self.path_output, f'{FN_PREFIX_WATERSTAND}_{Tx}.tif')
        validate_input(list(self._fn_waterstand_grid.values()))

        self.waterstand_grid = {}
        for herhalingstijd, fn in self._fn_waterstand_grid.items():
            with rasterio.open(fn, 'r') as EM:
                self.waterstand_grid[herhalingstijd] = EM.read(1).astype(float)
                if self.transform is None:
                    self.transform = EM.transform
        logging.info(
            f'Waterstand grids ingelezen voor: {self._fn_waterstand_grid.keys()}. Opgeslagen in variable waterstand_grid')

    def lees_waterdiepte_grids(self, waterdiepte_grids: dict = None):
        """
        Als de tool al eens (deels) is gerund, dan kan deze functie gebruikt worden om handmatig de overstromingsgrids
        in te lezen. Opbouw van de input dictionary is bijvoorbeeld:
        input = {'T10': 'padnaam/naar/Waterdiepte_T10.tif',
                 'T25': 'padnaam/naar/Waterdiepte_T25.tif',
                 etc.}
        De inputs worden 1 voor 1 ingelezen met rasterio en toegevoegd aan self.d_grid
        """

        if waterdiepte_grids is not None:
            self._fn_waterdiepte_grid = waterdiepte_grids
        elif self._fn_waterdiepte_grid is None:
            self._fn_waterdiepte_grid = {}
            for Tx in COL_LIST:
                self._fn_waterdiepte_grid[Tx] = os.path.join(
                    self.path_output, f'{FN_PREFIX_WATERDIEPTE}_{Tx}.tif')
        validate_input(list(self._fn_waterdiepte_grid.values()))

        self.waterdiepte_grid = {}
        for herhalingstijd, fn in self._fn_waterdiepte_grid.items():
            with rasterio.open(fn, 'r') as EM:
                self.waterdiepte_grid[herhalingstijd] = EM.read(
                    1).astype(float)
                if self.transform is None:
                    self.transform = EM.transform
        logging.info(
            f'waterdiepte grids ingelezen voor: {self._fn_waterdiepte_grid.keys()}. Opgeslagen in variable waterdiepte_grid')

    def _read_network(self, result_settings):

        ntw_objids = result_settings['ntw_nodes']
        fn_network = result_settings['fn_network_ntw']

        if fn_network.lower().endswith('.ntw'):
            network = Network.read_network_n(fn_network)

        network.rename(columns=lambda x: x.strip(), inplace=True)

        print(
            f'The following network nodetypes are used for analysis: {ntw_objids}')
        diff = set(ntw_objids).difference(network[COL_NODE_TYPE])
        if len(diff) > 0:
            print(
                f"The following nodetypes are not found: {list(diff)}. Please choose nodes from this list: {list(network[COL_NODE_TYPE].unique())}")
        network = network[network[COL_NODE_TYPE].isin(ntw_objids)]
        logging.info(f'Network loaded: {fn_network}')
        return network


            #raise NotImplementedError

    def _read_afwateringsgebieden(self):
        """Read afwateringsgebieden shape"""
        gebieden = set_crs(gpd.read_file(self.fn_gebieden), crs='EPSG:28992')
        logging.info(f'Afwateringsgebieden inladen: {self.fn_gebieden}')
        return gebieden


class Toetsing():
    def __init__(self, fn_hoogtegrid: str, output_dir="output", output_prefix=""):
        """Class voor het afleiden van de toetshoogtes in de watersysteemanalyse (WSA). 

        Args:
            fn_hoogtegrid (str): Pathname of the elevation raster
            output_dir (str, optional): Export folder. Defaults to "output".
            output_prefix (str): prefix for output
        """

        self.path_tussenresultaat = create_dir(
            os.path.join(output_dir, FOLDER_BEWERKTE_INPUT))
        self.export_path = create_dir(
            os.path.join(output_dir, FOLDER_TOETSING))
        self.peilgebieden_shp = None
        self.afwateenheid_shp = None
        self.ahn_rst = fn_hoogtegrid
        self.peilgebieden = None
        self.afwateenheid = None
        self.panden_mask = None
        self.watervlakken_mask = None
        self.normenraster = None
        self.prefix = output_prefix

    def inlezen_peilgebieden(self, peilgebieden_shp: str, peilgebieden_col_code: str = "CODE", peilgebieden_col_peil="WS_LAAGPEI", verwijder_peilgebieden_zonder_peil=True, selectie_code: list = None):
        """Inlezen van de shape met peilgebieden

        Args:
            peilgebieden_shp (str): bestandslocatie
            peilgebieden_col_code (str, optional): kolom met unieke id/code. Defaults to "CODE".
            peilgebieden_col_peil (str, optional): kolom met het streefpeil. Defaults to "WS_LAAGPEI".
            verwijder_peilgebieden_zonder_peil (bool, optional): optie om peilgebieden zonder peil te verwijderen uit de output. Defaults to True.
            selectie_code: Lijst met peilgebiedcodes als subselectie
        Returns:
            geopandas: Geometrie peilgebieden
        """

        validate_columns_in_shp(
            peilgebieden_shp, [peilgebieden_col_code, peilgebieden_col_peil])
        validate_crs(peilgebieden_shp)
        peilgebieden = gpd.read_file(peilgebieden_shp)
        peilgebieden = peilgebieden.to_crs(crs='EPSG:28992')

        peilgebieden.set_index(peilgebieden_col_code, inplace=True)
        if any(peilgebieden.index.duplicated()):
            raise Exception(f"ERROR: Duplicate codes in shapefile {peilgebieden_shp}: "
                            f"{peilgebieden[peilgebieden.index.duplicated()].index.to_list()}")

        peilgebieden[COL_PEIL] = peilgebieden[peilgebieden_col_peil].astype(
            'float')
        if verwijder_peilgebieden_zonder_peil:
            peilgebieden = peilgebieden.loc[~pd.isnull(
                peilgebieden[COL_PEIL]).values]
        if selectie_code is not None:
            peilgebieden = peilgebieden.loc[selectie_code]
        self.peilgebieden = peilgebieden

        # Export naar folder
        if self.path_tussenresultaat is not None:
            fn_name = os.path.join(
                self.path_tussenresultaat, self.prefix+os.path.basename(peilgebieden_shp))
        fn_name = fn_name.replace(".shp", "_selectie.shp")
        peilgebieden.to_file(fn_name)
        self.peilgebieden_shp = fn_name

        # Bijsnijden AHN o.b.v. peilgebieden shape
        self.ahn_rst = self.voorbewerken_ahn_raster(
            self.ahn_rst, self.peilgebieden_shp)
        return self.peilgebieden

    def inlezen_afwateringseenheden(self, afweenheid_shp: str, afweenheid_col_code: str = "AFWEENHEID",
                                    verwijder_peilgebieden_zonder_peil=True, overlap_threshold: float = 0.01):
        """Inlezen van de shape met afwateringseenheden. Voor het inlezen van de afwateringsgebieden moeten eerst de
        peilgebieden worden ingelezen.

        Args:
            afweenheid_shp (str): bestandslocatie
            afweenheid_col_code (str, optional): kolom met unieke id/code. Defaults to "AFWEENHEID".
            verwijder_peilgebieden_zonder_peil (bool, optional): optie om gebieden zonder peil te verwijderen uit de
            output. Defaults to True.
            overlap_threshold (float, optional): factor that a afweenheid is allowed to overlap with a second peilgebied

        Returns:
            geopandas: Geometrie peilgebieden
        """
        if self.peilgebieden is None:
            raise ValueError(
                "Peilgebieden nog niet ingelezen. Lees eerst de peilgebieden in")

        # Validate input
        validate_columns_in_shp(afweenheid_shp, [afweenheid_col_code])
        validate_crs(afweenheid_shp)

        # Inlezen afwaterinseenheden en kolom peil uit peilgebieden toevoegen
        afwat = gpd.read_file(afweenheid_shp)
        afwat = afwat.to_crs("EPSG:28992")
        afwat.set_index(afweenheid_col_code, inplace=True)
        if any(afwat.index.duplicated()):
            raise Exception(f"ERROR: Duplicate codes in shapefile {afweenheid_shp}: "
                            f"{afwat[afwat.index.duplicated()].index.to_list()}")

        validate_overlap_KAE_PG(afwat,
                                self.peilgebieden,
                                os.path.join(self.export_path, 'error_afwateringseenheden.shp'),
                                threshold=overlap_threshold)


        afwat['rep_point'] = afwat.geometry.representative_point()
        afwat = afwat.set_geometry('rep_point')
        afwat = afwat.sjoin(
            self.peilgebieden[[COL_PEIL, "geometry"]], how="left", predicate='covered_by')
        afwat = afwat.set_geometry('geometry')
        afwat.drop(columns=["index_right", "rep_point"], inplace=True)
        # Verwijder dubbelingen die ontstaan bij de spatial join
        afwat = afwat[~afwat.index.duplicated(keep='first')] #@TODO check why duplicates and is it correct to only keep first

        if verwijder_peilgebieden_zonder_peil:
            afwat = afwat.loc[~pd.isnull(afwat[COL_PEIL]).values]

        # Export naar folder
        if self.path_tussenresultaat is not None:
            fn_name = os.path.join(
                self.path_tussenresultaat, self.prefix+os.path.basename(afweenheid_shp))
        fn_name = fn_name.replace(".shp", "_selectie.shp")
        afwat.to_file(fn_name)
        self.afwateenheid_shp = fn_name

        self.afwateenheid = afwat
        return self.afwateenheid

    def voorbewerken_ahn_raster(self, ahn_rst, clip_shape):
        """Clip AHN raster tot de opgegeven shape

        Args:
            ahn_rst (_type_): bestandsloctatie (.tif)
            clip_shape (_type_): bestandslocatie shape/gpkg (.shp/.gpkg)

        Returns:
            str: bestandsnaam van het nieuwe raster
        """
        self.ahn_rst = clip_raster_to_shape(
            ahn_rst, clip_shape, export_folder=self.path_tussenresultaat)
        return self.ahn_rst

    def genereren_panden_mask(self, bgt_shp: str, bgt_col_functie: str = "FUNCTIE", bgt_functie_pand: list = ["pand"]):
        """
        Genereert bgt raster met panden
        Args:
            bgt_shp: Shape met de BGT
            bgt_col_functie: kolomnaam in de bgt shape met functies
            bgt_functie_pand: bgt functies die als pand worden meegenomen

        Returns: bestandslocatie nieuwe raster
        """
        if self.ahn_rst is None:
            raise ValueError(
                "Lees eerst het AHN in zodat dit raster op basis van de AHN uitgelijnd kan worden.")

        fn_bgt = os.path.join(self.path_tussenresultaat,
                              self.prefix+BGT_PANDEN_RST)
        if os.path.exists(fn_bgt):
            self.panden_mask = validate_raster_input(
                fn_bgt, self.ahn_rst, export_folder=self.path_tussenresultaat)
        else:
            validate_columns_in_shp(bgt_shp, [bgt_col_functie])
            validate_crs(bgt_shp)
            self.panden_mask = bgt_functie_to_rst(bgt_shp, filename_output=fn_bgt, reference_raster=self.ahn_rst,
                                                  bgt_col_functie=bgt_col_functie, bgt_functie_objecttypen=bgt_functie_pand)
        return self.panden_mask

    def genereren_watervlakken_mask(self, bgt_shp: str, bgt_col_functie: str = "FUNCTIE", bgt_functie_watervlak: list = ["waterloop", "watervlak"]):
        """
        Genereert bgt raster met panden
        Args:
            bgt_shp: Shape met de BGT
            bgt_col_functie: kolomnaam in de bgt shape met functies
            bgt_functie_watervlak: bgt typen die als watervlak worden meegenomen

        Returns: bestandslocatie nieuwe raster
        """
        if self.ahn_rst is None:
            raise ValueError(
                "Lees eerst het AHN in zodat dit raster op basis van de AHN uitgelijnd kan worden.")

        fn_bgt = os.path.join(
            self.path_tussenresultaat, self.prefix+BGT_WATERVLAKKEN_RST)
        if os.path.exists(fn_bgt):
            self.watervlakken_mask = validate_raster_input(
                fn_bgt, self.ahn_rst, export_folder=self.path_tussenresultaat)
        else:
            validate_columns_in_shp(bgt_shp, [bgt_col_functie])
            self.watervlakken_mask = bgt_functie_to_rst(
                bgt_shp, filename_output=fn_bgt, reference_raster=self.ahn_rst, bgt_col_functie=bgt_col_functie, bgt_functie_objecttypen=bgt_functie_watervlak)
        return self.watervlakken_mask

    def voorbewerken_normenraster(self, normen_rst):
        if self.ahn_rst is None:
            raise ValueError(
                "Lees eerst het AHN in zodat dit raster op basis van de AHN uitgelijnd kan worden.")
        self.normenraster = validate_raster_input(
            normen_rst, self.ahn_rst, export_folder=self.path_tussenresultaat)
        return self.normenraster

    def toetsing_berging(self, drempelhoogte = 0.1, percentages: list = [0.1, 1, 2, 5, 10, 15, 20], peilgebieden=True, afwateringsgebieden=False, Tx_percentage_toetshoogte={10: 5, 11: 10, 25: 1, 50: 1, 100: 0.1}):
        """Uitvoeren van de bergingstoets. Het waterpeil wordt stapsgewijs opgehoogd om te bepalen hoeveel inundatie er optreed bij de opgegeven percentages.
        Voor het uitvoeren van deze toets moeten de volgende preproces stappen zijn genomen, dit zijn functies in deze class:
        - inlezen_peilgebieden
        - optioneel: inlezen_afwateringseenheden
        - voorbewerken_ahn_raster
        - genereren_panden_mask
        - genereren_watervlakken_mask
        - voorbewerken_normenraster

        Args:
            drempelhoogte (_type_): Drempelhoogte waarmee het maaiveld t.p.v. panden worden opgehoogd. Defaults to 0.1.
            percentages (_type_): Percentages die als niveaus worden aangehouden bij uit te voeren kaart. Defaults to [1, 2, 5, 10, 15, 20].
            peilgebieden (bool, optional): Toetsing wel of niet uitvoeren voor peilgebieden. Defaults to True.
            afwateringsgebieden (bool, optional): Toetsing wel of niet uitvoeren voor afwateringsgebieden. Defaults to False.
            Tx_percentage_toetshoogte (dict): Dictionary met toegestaan percentage inundatie per normeringsklasse

        Raises:
            ValueError: als niet alle bestanden zijn ingeladen.

        """

        if self.ahn_rst is None:
            raise ValueError("AHN niet ingeladen")
        else:
            print(f"AHN raster: {self.ahn_rst}")
        if (self.peilgebieden is None) and peilgebieden:
            raise ValueError("Peilgebieden niet ingeladen")
        else:
            print(f"Toetsing wordt uitgevoerd voor Peilgebieden")
        if (self.afwateenheid is None) and afwateringsgebieden:
            raise ValueError("Afwateringseenheden niet ingeladen")
        else:
            print(f"Toetsing wordt uitgevoerd voor Afwateringseenheden")
        if self.panden_mask is None:
            raise ValueError("BGT panden niet ingeladen")
        else:
            print(f"Masker panden: {self.panden_mask}")
        if self.watervlakken_mask is None:
            raise ValueError("BGT watervlakken niet ingeladen")
        else:
            print(f"Masker watervlakken: {self.watervlakken_mask}")
        if self.normenraster is None:
            raise ValueError("Normenraster niet ingeladen")
        else:
            print(f"Normen raster: {self.normenraster}")

        peilstijgingen = np.r_[
            np.arange(0.02, 0.25, 0.01), np.arange(0.25, 2.0, 0.05), 10]

        fn = None
        fn_afw = None
        if peilgebieden:
            # volumes = pd.DataFrame(index=np.array(peilstijgingen).astype(
            #     np.float32), columns=self.peilgebieden.index.tolist())
            print("Start toetsing voor peilgebieden")
            raster_fn = {}
            for idx, gdf_gebied in tqdm(self.peilgebieden.iterrows(), total=len(self.peilgebieden)):
                raster_fn[idx] = toetsinganalyse(
                    gebied_id=idx,
                    geom=gdf_gebied["geometry"],
                    drempelhoogte=drempelhoogte,
                    peil=gdf_gebied["peil"],
                    path_export=self.export_path,
                    watervlakken_raster=self.watervlakken_mask,
                    norm_raster=self.normenraster,
                    dem_raster=self.ahn_rst,
                    panden_raster=self.panden_mask,
                    peilstijgingen=peilstijgingen,
                    # volumes=volumes,
                    percentages=percentages)

            fn = tabel_toetsingsanalyse(percentages=percentages, gebieden=self.peilgebieden,
                                        path_export=self.export_path, fn_naam=self.prefix+"Toetshoogte_peilgebieden", peilstijgingen=peilstijgingen, Tx_percentage_toetshoogte=Tx_percentage_toetshoogte)
            print(
                f"Samenvattende tabel voor peilgebieden weggeschreven naar {fn}")

            # Stitch rasters together
            for norm in list(T_LIST_DICT.keys()):
                raster_list = []
                for key, file_dict in raster_fn.items():
                    try:
                        raster_list.append(file_dict[norm])
                    except KeyError:
                        print(f'Peilgebied {key} bevat geen norm {norm}, sla raster over.')
                        pass

                export_fn = f'Maaiveldpercentage_{norm}'
                mosaic_raster(fnames=raster_list, filename=export_fn, export_folder=self.export_path, clip_polygon=None)

            print(
                f"Samengevoegd maaiveldpercentageraster voor norm {norm} weggeschreven naar vattende tabel voor peilgebieden weggeschreven naar {os.path.join(self.export_path, export_fn)}")


        if afwateringsgebieden:
            # volumes = pd.DataFrame(index=np.array(peilstijgingen).astype(
            #     np.float32), columns=self.afwateenheid.index.tolist())
            print("Start toetsing voor Afwateringsgebieden")
            for idx, gdf_gebied in tqdm(self.afwateenheid.iterrows(), total=len(self.afwateenheid)):
                toetsinganalyse(
                    gebied_id=idx,
                    geom=gdf_gebied["geometry"],
                    drempelhoogte=drempelhoogte,
                    peil=gdf_gebied["peil"],
                    path_export=self.export_path,
                    watervlakken_raster=self.watervlakken_mask,
                    norm_raster=self.normenraster,
                    dem_raster=self.ahn_rst,
                    panden_raster=self.panden_mask,
                    peilstijgingen=peilstijgingen,
                    # volumes=volumes,
                    percentages=percentages)
            fn_afw = tabel_toetsingsanalyse(percentages=percentages, gebieden=self.afwateenheid,
                                            path_export=self.export_path, fn_naam=self.prefix+"Toetshoogte_afwateringseenheden", peilstijgingen=peilstijgingen, Tx_percentage_toetshoogte=Tx_percentage_toetshoogte)
            print(
                f"Samenvattende tabel voor afwateringseenheden weggeschreven naar {fn_afw}")

        print("Toetsingsanalyse voltooid")
        return fn, fn_afw