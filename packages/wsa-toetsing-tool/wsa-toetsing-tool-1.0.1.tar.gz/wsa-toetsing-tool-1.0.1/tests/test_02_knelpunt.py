import unittest
import pytest

import geopandas as gpd
import geopandas.testing as gpd_testing
import pandas as pd
import rasterio
import numpy as np

from wsa_toetsing_tool.wsa_delfland.wsa import Knelpunten
import configparser
import os
import warnings
from matplotlib._api.deprecation import MatplotlibDeprecationWarning

pd.options.mode.chained_assignment = None  # default='warn'
warnings.filterwarnings("ignore",category=MatplotlibDeprecationWarning)

settings = './data/input/settings.ini'
scenario_settings = './data/input/settings_huidig.ini'


@pytest.mark.filterwarnings("ignore:overflow encountered in exp")
class TestKnelpunten(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        input_path = os.path.dirname(settings)

        config = configparser.ConfigParser(inline_comment_prefixes="#")
        config.read(settings)

        scenario_config = configparser.ConfigParser(inline_comment_prefixes="#")
        scenario_config.read(scenario_settings)

        wsa_titel = config['output']['wsa_titel']  # Titel van deze wsa
        klimaatscenario = scenario_config['scenario']['naam']  # wordt ltoegevoegd aan de naam van de knelpuntenmap

        # Export path
        output_dir = config['output']['folder_pad']  # map waarin resultaten worden weggeschreven
        prefix_output = config['output'][
            'prefix']  # prefix voor alle output bestanden, mag ook leeg een lege string zijn: ""

        # Normenraster
        fn_normen_rst = os.path.join(input_path,
                                     config['normen']['bestand_pad'])  # Raster met normering (10, 11, 25, 50, 100)

        # Hoogteraster
        fn_hoogtegrid = os.path.join(input_path, config['hoogtemodel'][
            'bestand_pad'])  # Raster met het AHN (*.tif), resolutie 0,5m, projectie RDNEW (EPSG 22892)

        # Peilgebieden
        fn_peilgebieden = os.path.join(input_path, config['peilgebieden']['bestand_pad'])
        peilgebieden_col_code = config['peilgebieden']['kolomnaam_peilgebied_code']
        initieel_peil_kolom = config['peilgebieden'][
            'kolomnaam_peilgebied_peil_statistiek']  # 'WS_HOOGP_1' # Kolom met het initiele peil, voor de bepaling van waterstandsstijging

        # Afwateringsgebieden
        fn_afwateringsgebieden = os.path.join(input_path, config['afwateringseenheden'][
            'bestand_pad'])  # Shape met afwateringseenheden
        afweenheid_col_code = config['afwateringseenheden']['kolomnaam_afwateringseenheid_code']

        # BGT en toetsnormen
        bgt_shp = os.path.join(input_path, config['bgt']['bestand_pad'])
        bgt_col_functie = config['bgt']['kolomnaam_functie']
        bgt_functie_pand = config['bgt']['functie_pand']
        bgt_functie_watervlak = config['bgt']['functie_watervlak']
        bgt_functie_watervlak = bgt_functie_watervlak.split(',')
        bgt_functie_watervlak = [item.strip() for item in bgt_functie_watervlak]

        # Toetshoogte
        fn_toetshoogte_peilgebied = f"{output_dir}/Toetsing/{prefix_output}Toetshoogte_peilgebieden.shp"
        fn_toetshoogte_afwateringsgebied = f"{output_dir}/Toetsing/{prefix_output}Toetshoogte_afwateringseenheden.shp"

        # Read modelpakket, make it lower case and strip non-alphabetical characters
        modelpakket = "".join([char for char in scenario_config['scenario']['modelpakket'].lower() if char.isalpha()])

        result_settings = {'modelpakket': modelpakket}
        # Sobek model
        if modelpakket == 'sobek':
            fn_calcpnt_his_unstripped = scenario_config['scenario']['his_file'].split(
                ',')  # CALCPNT.HIS. Mag ook een lijst zijn met meerdere CALCPNT.HIS onder de voorwaarde dat het netwerk en de output parameters exact gelijk zijn, en de tijdsreeks aansluitend is. De tijdreeksen worden samengevoegd tot 1 reeks. Er vindt geen controle plaats op consistentie.
            fn_calcpnt_his = [os.path.join(input_path, s.strip()) for s in fn_calcpnt_his_unstripped]

            fn_network_ntw = os.path.join(input_path, scenario_config['scenario']['ntw_file'])  # NETWORK.NTW
            calcpnt_par_statistiek = scenario_config['scenario'][
                'parameter']  # Parameters in CALCPNT.HIS waarop de statistiek plaatsvindt

            ntw_nodes_unstripped = scenario_config['scenario']['ntw_nodes'].split(
                ',')  # ["SBK_GRIDPOINTFIXED", "SBK_GRIDPOINT", "SBK_CHANNELCONNECTION", "SBK_CHANNEL_STORCONN&LAT"]
            ntw_nodes = [s.strip() for s in ntw_nodes_unstripped]
            dhydro_result_folder = None

            result_settings['fn_calcpnt_his'] = fn_calcpnt_his
            result_settings['fn_network_ntw'] = fn_network_ntw
            result_settings['calcpnt_par_statistiek'] = calcpnt_par_statistiek
            result_settings['ntw_nodes'] = ntw_nodes
        elif modelpakket == 'dhydro':

            result_settings['dhydro_result_folder'] = os.path.join(input_path,
                                                                   scenario_config['scenario']['resultaat_folder'])
            result_settings['max_wl_var'] = scenario_config['scenario']['fou_max_wl_variabele']
            result_settings['max_wl_time_var'] = scenario_config['scenario']['fou_max_wl_tijd_variabele']
            result_settings['exclude_boundary_nodes'] = eval(scenario_config['scenario']['exclude_boundary_nodes'])
            result_settings['boundary_conditions_file'] = os.path.join(input_path, scenario_config['scenario'][
                'boundary_conditions_file'])

        else:
            raise NotImplementedError(f"Modelpakket {modelpakket} in scenarioconfiguratie niet geimplementeerd")

        # Waterstandsstatistiek
        drop_rows_with_nodata = eval(scenario_config['statistiek'][
                                         'negeer_nodata'])  # True of False. Verwijder rekenpunten waarvoor geen waterstandsstatistiek is uitgevoerd

        exclude_nodes_unstripped = scenario_config['statistiek']['negeer_nodes'].split(
            ',')  # None of lijst van nodes die uitgezonderd moeten worden van de analyse, bv ["id_node1", "10"]
        exclude_nodes = [s.strip() for s in exclude_nodes_unstripped]

        gumbel_plots = eval(scenario_config['statistiek'][
                                'plot_gumbel'])  # True of False. Gumbel plots vertragen het afleiden van de waterstandsstatistiek significant.
        n_jaren_plotposities = eval(scenario_config['statistiek'][
                                        'aantal_jaren_plotposities'])  # None of integer. Aantal jaren waarvoor de opgeven waterstandsreeks representatief is voor de Gumbel statistiek.
        methode_agg_rekenpunt = scenario_config['statistiek'][
            'aggregatie_methode']  # min, max, mean, median. Parameter waarmee het het peil per gebied wordt bepaald op basis van de rekenpunten

        # Definitie periode groeiseizoen
        start_day = eval(scenario_config['periode_groeiseizoen']['start_dag'])
        start_month = eval(scenario_config['periode_groeiseizoen']['start_maand'])
        end_day = eval(scenario_config['periode_groeiseizoen']['eind_dag'])
        end_month = eval(scenario_config['periode_groeiseizoen']['eind_maand'])
        periode_groeiseizoen = [(start_month, start_day), (end_month, end_day)]  # [(mm, dd), (mm, dd)]

        # Handmatig opgeven waterstandsstatistiek.
        fn_calcpunt_stat_overrule = scenario_config.get('handmatige_statistiek', 'bestand_pad')
        if fn_calcpunt_stat_overrule != "":
            fn_calcpunt_stat_overrule = os.path.join(input_path,
                                                     scenario_config.get('handmatige_statistiek', 'bestand_pad'))

        stat_columns = {
            scenario_config['handmatige_statistiek']['kolomnaam_T10']: 'T10',
            scenario_config['handmatige_statistiek']['kolomnaam_T10_GROEI']: 'T10_GROEI',
            scenario_config['handmatige_statistiek']['kolomnaam_T25']: 'T25',
            scenario_config['handmatige_statistiek']['kolomnaam_T30']: 'T30',
            scenario_config['handmatige_statistiek']['kolomnaam_T50']: 'T50',
            scenario_config['handmatige_statistiek']['kolomnaam_T100']: 'T100',
        }  # key is name in file, value is one of these values ['T10','T10_GROEI','T25', 'T50', 'T100']

        # Inladen en valideren inputparameters - code hieronder niet aanpassen
        wsa = Knelpunten(fn_afwateringsgebieden,
                         fn_hoogtegrid,
                         output_dir,
                         prefix_output,
                         klimaatscenario=klimaatscenario,
                         wsa_titel=wsa_titel)

        ####################################################
        if fn_calcpunt_stat_overrule:
            wsa.importeer_waterstandsstatistiek(fn_calcpunt_stat_overrule, stat_dict=stat_columns)
        else:
            wsa.genereer_waterstandsstatistiek(result_settings,
                                               periode_groeiseizoen,
                                               plots=gumbel_plots,
                                               exclude_id=exclude_nodes,
                                               drop_rows_with_nodata=drop_rows_with_nodata,
                                               n_jaren_plotposities=n_jaren_plotposities,
                                               )

            fn_sortering_events = os.path.join(wsa.path_output,
                                               f"statistiek/{prefix_output}sortering_events_{klimaatscenario}.xlsx")
            wsa.exporteer_sortering_events(fn_sortering_events)
        wsa.waterstandsstatistiek.head()


        ####################################################

        wsa.genereer_peil_per_gebied(par=methode_agg_rekenpunt, additional_pars=[])
        wsa.peil_per_gebied.head()

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="overflow encountered in exp")
            fn_herhalingstijd = os.path.join(wsa.path_output,
                                             f"statistiek/{prefix_output}herhalingstijd_inundatie_{klimaatscenario}.tif")
            wsa.genereer_herhalingstijd_raster(fn_herhalingstijd=fn_herhalingstijd)

        ####################################################

        # Lees toetspeil in
        # wsa.lees_toetshoogte_afwateringsgebieden(fn_toetshoogte_afwateringsgebied)

        ####################################################


        fn_waterstandsrasters = wsa.genereer_waterstandsrasters(initieel_peil_kolom=initieel_peil_kolom)
        fn_waterdiepterasters = wsa.genereer_waterdiepterasters(fn_waterstandsrasters, drempel_diepte=0.01)

        ###################################################

        fn_waterstandsrasters_toetshoogte = wsa.genereer_waterstandsrasters(fn_toetshoogte_peilgebied,
                                                                            fn_suffix='_toets')
        fn_waterdiepterasters_toetshoogte = wsa.genereer_waterdiepterasters(fn_waterstandsrasters_toetshoogte,
                                                                            drempel_diepte=0.01,
                                                                            fn_suffix='_toets')

        ####################################################

        fn_waterdiepteverschilrasters = wsa.genereer_verschilrasters(fn_waterdiepterasters, referentie='initieel')
        fn_waterdiepteverschilrasters_toetshoogte = wsa.genereer_verschilrasters(fn_waterdiepterasters,
                                                                                 referentie=fn_waterdiepterasters_toetshoogte,
                                                                                 ref_suffix='toets',
                                                                                 nodata_to_zero=False)

        fn_toename_volume_per_peilgebied = wsa.bepaal_toename_volume(fn_waterdiepteverschilrasters,
                                                                     fn_peilgebieden,
                                                                     code_column=peilgebieden_col_code,
                                                                     output_filename='Volumetoename_peilgebieden')
        fn_toename_volume_per_kae = wsa.bepaal_toename_volume(fn_waterdiepteverschilrasters,
                                                              fn_afwateringsgebieden,
                                                              code_column=afweenheid_col_code,
                                                              output_filename='Volumetoename_afwateringsgebieden')

        fn_volume_boven_toetshoogte_per_peilgebied = wsa.bepaal_toename_volume(
            fn_waterdiepteverschilrasters_toetshoogte,
            fn_peilgebieden,
            code_column=peilgebieden_col_code,
            output_filename='Volume_boven_toetshoogte_peilgebieden')

        bgt_rst = wsa.genereren_watervlakken_mask(bgt_shp=bgt_shp, bgt_col_functie=bgt_col_functie,
                                                  bgt_functie_watervlak=bgt_functie_watervlak)
        fn_waterdiepte_filter = wsa.filter_waterdiepteraster_raakt_watergang(bgt_rst, fn_waterdiepterasters)
        ####################################################
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="CRS not set for some of the concatenation inputs")
            warnings.filterwarnings("ignore", message="Column names longer than 10 characters will be truncated when saved to ESRI Shapefile")
            fn_knelpunten_shp, fn_waterdiepte_norm = wsa.genereer_knelpunten_shape(fn_normen_rst, fn_waterdiepte_filter,
                                                                                   fn_peilgebieden)

        print("Ready initializing the test")

    @pytest.mark.run(order=3)
    def test_statistiek_rekenpunten(self):
        """
        Test if the statistics per calculation point derived from the models are unaltered
        """
        output_data = gpd.read_file(fr'data/output/Knelpunten_huidig/statistiek/test_waterstandsstatistiek_huidig.shp')
        assert_data = gpd.read_file(r'data/assert/Knelpunten_huidig/statistiek/test_waterstandsstatistiek_huidig.shp')

        gpd_testing.assert_geodataframe_equal(output_data, assert_data)

    @pytest.mark.run(order=4)
    def test_statistiek_gebieden(self):
        """
        Test if the statistics-aggregation to peilgebiedenis unaltered
        """
        output_data = gpd.read_file(r'data/output/Knelpunten_huidig/statistiek/test_gebieden_statistiek_huidig.shp')
        assert_data = gpd.read_file(r'data/assert/Knelpunten_huidig/statistiek/test_gebieden_statistiek_huidig.shp')

        gpd_testing.assert_geodataframe_equal(output_data, assert_data)

    @pytest.mark.run(order=5)
    def test_rasters(self):
        output_folder = r'data/output/Knelpunten_huidig'
        assert_folder = r'data/assert/Knelpunten_huidig'

        files = ['waterstandrasters/test_gebieden_waterstand_initieel.tif',
                 'waterstandrasters/test_gebieden_waterstand_T10.tif',
                 'waterstandrasters/test_gebieden_waterstand_T10_GROEI.tif',
                 'waterstandrasters/test_gebieden_waterstand_T10_GROEI_toets.tif',
                 'waterstandrasters/test_gebieden_waterstand_T10_toets.tif',
                 'waterstandrasters/test_gebieden_waterstand_T25.tif',
                 'waterstandrasters/test_gebieden_waterstand_T25_toets.tif',
                 'waterstandrasters/test_gebieden_waterstand_T50.tif',
                 'waterstandrasters/test_gebieden_waterstand_T50_toets.tif',
                 'waterstandrasters/test_gebieden_waterstand_T100.tif',
                 'waterstandrasters/test_gebieden_waterstand_T100_toets.tif',
                 
                 'waterdiepterasters/test_gebieden_waterdiepte_initieel.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T10.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T10_GROEI.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T10_GROEI_toets.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T10_toets.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T25.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T25_toets.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T50.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T50_toets.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T100.tif',
                 'waterdiepterasters/test_gebieden_waterdiepte_T100_toets.tif',

                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T10_GROEI-referentie.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T10_GROEI-toets.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T10-referentie.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T10-toets.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T25-referentie.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T25-toets.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T50-referentie.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T50-toets.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T100-referentie.tif',
                 'waterdiepte_verschilrasters/test_gebieden_waterdiepte_verschil_T100-toets.tif',
                 ]

        for file in files:
            fn_output_file = os.path.join(output_folder, file)
            fn_assert_file = os.path.join(assert_folder, file)

            with rasterio.open(fn_output_file) as output_file:
                output_data = output_file.read(1)
            with rasterio.open(fn_assert_file) as assert_file:
                assert_data = assert_file.read(1)  # Read the first band

            assert output_data.shape == assert_data.shape, f"Raster dimensions do not match: {file}"
            assert np.allclose(output_data, assert_data, atol=0.0001, equal_nan=True), f"Raster pixel values do not match: {file}"

    @pytest.mark.run(order=6)
    def test_volumetoename(self):
        """
        Test if the statistics-aggregation to peilgebiedenis unaltered
        """
        output_folder = r'data/output/Knelpunten_huidig/volumetoename'
        assert_folder = r'data/assert/Knelpunten_huidig/volumetoename'

        files = [
            'test_Volume_boven_toetshoogte_peilgebieden_huidig.shp',
            'test_Volumetoename_afwateringsgebieden_huidig.shp',
            'test_Volumetoename_peilgebieden_huidig.shp'
        ]

        for file in files:
            output_data = gpd.read_file(os.path.join(output_folder, file))
            assert_data = gpd.read_file(os.path.join(assert_folder, file))

            gpd_testing.assert_geodataframe_equal(output_data, assert_data)

    # @pytest.mark.run(order=7)
    # def test_knelpunten(self):

if __name__ == '__main__':
    unittest.main()