# imports
from wsa_toetsing_tool.wsa import Knelpunten
from wsa_toetsing_tool.config import COL_LIST_STAT, METHODE_AGGREGATIE_GEBIED
import os
import plotly.express as px
import configparser
import matplotlib.pyplot as plt
import rioxarray as rxr

import warnings
import argparse


def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='De knelpuntanalyse bepaalt de waterstandstatistiek en de knelpunten.')
    parser.add_argument('--settings', type=str, default="example_data/settings.ini", help='Path to the settings file')
    parser.add_argument('--scenario_settings', type=str, default="example_data/settings_toekomstig.ini", help='Path to the scenario settings file')

    # Parse arguments
    args = parser.parse_args()

    # Use the provided settings file path
    settings = args.settings
    scenario_settings = args.scenario_settings

    base_path = os.path.dirname(settings)

    # Check if settings file exists
    if not os.path.exists(settings):
        raise FileNotFoundError(f"Settings file '{settings}' not found")
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(settings)

    # Check if settings file exists
    if not os.path.exists(scenario_settings):
        raise FileNotFoundError(f"Scenario settings file '{settings}' not found")
    scenario_config = configparser.ConfigParser(inline_comment_prefixes="#")
    scenario_config.read(scenario_settings)


    wsa_titel = config['output']['wsa_titel'] # Titel van deze wsa
    klimaatscenario = scenario_config['scenario']['naam']# wordt ltoegevoegd aan de naam van de knelpuntenmap

    # Export path
    output_dir = os.path.join(base_path, config['output']['folder_pad']) # map waarin resultaten worden weggeschreven
    prefix_output = config['output']['prefix'] # prefix voor alle output bestanden, mag ook leeg een lege string zijn: ""

    # Normenraster
    fn_normen_rst = os.path.join(base_path, config['normen']['bestand_pad']) # Raster met normering (10, 11, 25, 50, 100)

    # Hoogteraster
    fn_hoogtegrid = os.path.join(base_path, config['hoogtemodel']['bestand_pad']) # Raster met het AHN (*.tif), resolutie 0,5m, projectie RDNEW (EPSG 22892)

    # Peilgebieden
    fn_peilgebieden = os.path.join(base_path, config['peilgebieden']['bestand_pad'])
    peilgebieden_col_code = config['peilgebieden']['kolomnaam_peilgebied_code']

    # Afwateringsgebieden
    fn_afwateringsgebieden = os.path.join(base_path, config['afwateringseenheden']['bestand_pad']) # Shape met afwateringseenheden
    afweenheid_col_code = config['afwateringseenheden']['kolomnaam_afwateringseenheid_code']
    initieel_peil_kolom = config['afwateringseenheden']['kolomnaam_peilgebied_peil_statistiek'] #'WS_HOOGP_1' # Kolom met het initiele peil, voor de bepaling van waterstandsstijging

    # BGT en toetsnormen
    bgt_shp = os.path.join(base_path, config['bgt']['bestand_pad'])
    bgt_col_functie = config['bgt']['kolomnaam_functie']
    bgt_functie_pand = config['bgt']['functie_pand']
    bgt_functie_watervlak = config['bgt']['functie_watervlak']
    bgt_functie_watervlak = bgt_functie_watervlak.split(',')
    bgt_functie_watervlak = [item.strip() for item in bgt_functie_watervlak]

    # Toetshoogte
    fn_toetshoogte_peilgebied = os.path.join(base_path, scenario_config['toetshoogte']['bestand_pad'])

    # Read modelpakket, make it lower case and strip non-alphabetical characters
    modelpakket = "".join([char for char in scenario_config['scenario']['modelpakket'].lower() if char.isalpha()])

    result_settings = {'modelpakket': modelpakket}
    # Sobek model
    if modelpakket == 'sobek':
        fn_calcpnt_his_unstripped = scenario_config['scenario']['his_file'].split(',') # CALCPNT.HIS. Mag ook een lijst zijn met meerdere CALCPNT.HIS onder de voorwaarde dat het netwerk en de output parameters exact gelijk zijn, en de tijdsreeks aansluitend is. De tijdreeksen worden samengevoegd tot 1 reeks. Er vindt geen controle plaats op consistentie.
        fn_calcpnt_his = [os.path.join(base_path, s.strip()) for s in fn_calcpnt_his_unstripped]

        fn_network_ntw = os.path.join(base_path, scenario_config['scenario']['ntw_file']) # NETWORK.NTW
        calcpnt_par_statistiek = scenario_config['scenario']['parameter'] # Parameters in CALCPNT.HIS waarop de statistiek plaatsvindt

        ntw_nodes_unstripped = scenario_config['scenario']['ntw_nodes'].split(',')# ["SBK_GRIDPOINTFIXED", "SBK_GRIDPOINT", "SBK_CHANNELCONNECTION", "SBK_CHANNEL_STORCONN&LAT"]
        ntw_nodes = [s.strip() for s in ntw_nodes_unstripped]
        dhydro_result_folder = None

        result_settings['fn_calcpnt_his'] = fn_calcpnt_his
        result_settings['fn_network_ntw'] = fn_network_ntw
        result_settings['calcpnt_par_statistiek'] = calcpnt_par_statistiek
        result_settings['ntw_nodes'] = ntw_nodes
    elif modelpakket == 'dhydro':

        result_settings['dhydro_result_folder'] = os.path.join(base_path, scenario_config['scenario']['resultaat_folder'])
        result_settings['max_wl_var'] = scenario_config['scenario']['fou_max_wl_variabele']
        result_settings['max_wl_time_var'] = scenario_config['scenario']['fou_max_wl_tijd_variabele']
        result_settings['exclude_boundary_nodes'] = eval(scenario_config['scenario']['exclude_boundary_nodes'])
        result_settings['boundary_conditions_file'] = os.path.join(base_path, scenario_config['scenario']['boundary_conditions_file'])

    else:
        raise NotImplementedError(f"Modelpakket {modelpakket} in scenarioconfiguratie niet geimplementeerd")


    # Waterstandsstatistiek
    drop_rows_with_nodata = eval(scenario_config['statistiek']['negeer_nodata']) # True of False. Verwijder rekenpunten waarvoor geen waterstandsstatistiek is uitgevoerd

    exclude_nodes_unstripped = scenario_config['statistiek']['negeer_nodes'].split(',') # None of lijst van nodes die uitgezonderd moeten worden van de analyse, bv ["id_node1", "10"]
    exclude_nodes = [s.strip() for s in exclude_nodes_unstripped]

    gumbel_plots = eval(scenario_config['statistiek']['plot_gumbel']) # True of False. Gumbel plots vertragen het afleiden van de waterstandsstatistiek significant.
    n_jaren_plotposities = eval(scenario_config['statistiek']['aantal_jaren_plotposities']) # None of integer. Aantal jaren waarvoor de opgeven waterstandsreeks representatief is voor de Gumbel statistiek.
    methode_agg_rekenpunt = scenario_config['statistiek']['aggregatie_methode'] #min, max, mean, median. Parameter waarmee het het peil per gebied wordt bepaald op basis van de rekenpunten

    # Definitie periode groeiseizoen
    start_day = eval(scenario_config['periode_groeiseizoen']['start_dag'])
    start_month = eval(scenario_config['periode_groeiseizoen']['start_maand'])
    end_day = eval(scenario_config['periode_groeiseizoen']['eind_dag'])
    end_month = eval(scenario_config['periode_groeiseizoen']['eind_maand'])
    periode_groeiseizoen = [(start_month, start_day), (end_month, end_day)] # [(mm, dd), (mm, dd)]

    # Handmatig opgeven waterstandsstatistiek.
    fn_calcpunt_stat_overrule = scenario_config.get('handmatige_statistiek', 'bestand_pad')
    if fn_calcpunt_stat_overrule != "":
        fn_calcpunt_stat_overrule = os.path.join(base_path, scenario_config.get('handmatige_statistiek', 'bestand_pad'))


    stat_columns = {
        scenario_config['handmatige_statistiek']['kolomnaam_T10']: 'T10',
        scenario_config['handmatige_statistiek']['kolomnaam_T10_GROEI']: 'T10_GROEI',
        scenario_config['handmatige_statistiek']['kolomnaam_T25']: 'T25',
        scenario_config['handmatige_statistiek']['kolomnaam_T30']: 'T30',
        scenario_config['handmatige_statistiek']['kolomnaam_T50']: 'T50',
        scenario_config['handmatige_statistiek']['kolomnaam_T100']: 'T100',
    } #key is name in file, value is one of these values ['T10','T10_GROEI','T25', 'T50', 'T100']

    # Inladen en valideren inputparameters - code hieronder niet aanpassen
    wsa = Knelpunten(fn_afwateringsgebieden,
                    fn_hoogtegrid,
                    output_dir,
                    prefix_output,
                    klimaatscenario=klimaatscenario,
                    wsa_titel=wsa_titel)

    # Read or create statistics
    if fn_calcpunt_stat_overrule:
        wsa.importeer_waterstandsstatistiek(fn_calcpunt_stat_overrule, stat_dict=stat_columns)
    else:
        wsa.genereer_waterstandsstatistiek(result_settings,
                                        periode_groeiseizoen,
                                        afweenheid_col_code,
                                        plots=gumbel_plots,
                                        exclude_id=exclude_nodes,
                                        drop_rows_with_nodata=drop_rows_with_nodata,
                                        n_jaren_plotposities=n_jaren_plotposities,
                                        )

        fn_sortering_events = os.path.join(wsa.path_output, f"statistiek/{prefix_output}sortering_events_{klimaatscenario}.xlsx")
        wsa.exporteer_sortering_events(fn_sortering_events)

    # Create html maps
    warnings.filterwarnings('ignore')
    waterstandstatistiek_epsg4326 = wsa.waterstandsstatistiek.to_crs('epsg:4326')
    fig = px.scatter_mapbox(waterstandstatistiek_epsg4326, color="T10", lat=waterstandstatistiek_epsg4326.geometry.y,
                            lon=waterstandstatistiek_epsg4326.geometry.x,
                    color_continuous_scale='Blues', size_max=15, zoom=12, mapbox_style='open-street-map', hover_data=COL_LIST_STAT)
    fig.show()
    fn_export_tmp = os.path.join(wsa.path_output, f"statistiek/{prefix_output}waterstandsstatistiek_{klimaatscenario}.html")
    fig.write_html(fn_export_tmp)

    # Generate water levels per area
    wsa.genereer_peil_per_gebied(par=methode_agg_rekenpunt, additional_pars=METHODE_AGGREGATIE_GEBIED)

    # Generate return period raster
    fn_herhalingstijd = os.path.join(wsa.path_output, f"statistiek/{prefix_output}herhalingstijd_inundatie_{klimaatscenario}.tif")
    wsa.genereer_herhalingstijd_raster(fn_herhalingstijd=fn_herhalingstijd)

    peil_per_gebied_epsg4326 = wsa.peil_per_gebied.to_crs('epsg:4326')

    # Generate water level and depth rasters of return periods and toetshoogte
    fn_waterstandsrasters = wsa.genereer_waterstandsrasters(initieel_peil_kolom=initieel_peil_kolom)
    fn_waterdiepterasters= wsa.genereer_waterdiepterasters(fn_waterstandsrasters, drempel_diepte=0.01)

    fn_waterstandsrasters_toetshoogte = wsa.genereer_waterstandsrasters(fn_toetshoogte_peilgebied,
                                                                        fn_suffix='_toets')
    fn_waterdiepterasters_toetshoogte = wsa.genereer_waterdiepterasters(fn_waterstandsrasters_toetshoogte,
                                                                        drempel_diepte=0.01,
                                                                        fn_suffix='_toets')

    # Generate difference rasters
    fn_waterdiepteverschilrasters = wsa.genereer_verschilrasters(fn_waterdiepterasters, referentie='initieel')
    fn_waterdiepteverschilrasters_toetshoogte = wsa.genereer_verschilrasters(fn_waterdiepterasters,
                                                                            referentie=fn_waterdiepterasters_toetshoogte,
                                                                            ref_suffix='toets',
                                                                            nodata_to_zero=False)
    # Generate volume increase per area
    fn_toename_volume_per_peilgebied = wsa.bepaal_toename_volume(fn_waterdiepteverschilrasters,
                                                                fn_peilgebieden,
                                                                code_column=peilgebieden_col_code,
                                                                output_filename='Volumetoename_peilgebieden')
    fn_toename_volume_per_kae = wsa.bepaal_toename_volume(fn_waterdiepteverschilrasters,
                                                        fn_afwateringsgebieden,
                                                        code_column=afweenheid_col_code,
                                                        output_filename='Volumetoename_afwateringsgebieden')

    # Generate volume above toetshoogte per area
    fn_volume_boven_toetshoogte_per_peilgebied = wsa.bepaal_toename_volume(fn_waterdiepteverschilrasters_toetshoogte,
                                                                fn_peilgebieden,
                                                                code_column=peilgebieden_col_code,
                                                                output_filename='Volume_boven_toetshoogte_peilgebieden')

    # Generate knelpunten
    bgt_rst = wsa.genereren_watervlakken_mask(bgt_shp=bgt_shp, bgt_col_functie=bgt_col_functie, bgt_functie_watervlak=bgt_functie_watervlak)
    fn_waterdiepte_filter = wsa.filter_waterdiepteraster_raakt_watergang(bgt_rst, fn_waterdiepterasters)
    fn_knelpunten_shp, fn_waterdiepte_norm = wsa.genereer_knelpunten_shape(fn_normen_rst, fn_waterdiepte_filter, fn_peilgebieden)

if __name__ == "__main__":
    main()