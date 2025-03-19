import os
import geopandas as gpd
import configparser
import numpy as np
import argparse

def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='Run WSA Toetsing Tool')
    parser.add_argument('--settings', type=str, default="example_data/settings.ini", help='Path to the settings file')
    parser.add_argument('--reference_scenario_settings', type=str, default="example_data/settings_huidig.ini", help='Path to the reference scenario settings file')
    parser.add_argument('--scenario_settings', type=str, default="example_data/settings_toekomstig.ini", help='Path to the compared scenario settings file')

    # Parse arguments
    args = parser.parse_args()

    settings = args.settings
    reference_scenario_settings = args.reference_scenario_settings
    scenario_settings = args.scenario_settings
    # TODO: check if the scenario settings are different from the reference settings

    # Load settings
    base_path = os.path.dirname(settings)

    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(settings)

    reference_scenario_config = configparser.ConfigParser(inline_comment_prefixes="#")
    reference_scenario_config.read(reference_scenario_settings)

    scenario_config = configparser.ConfigParser(inline_comment_prefixes="#")
    scenario_config.read(scenario_settings)

    fn_afwateringsgebied = os.path.join(base_path, config['afwateringseenheden']['bestand_pad'])
    afwateringsgebied_code = config['afwateringseenheden']['kolomnaam_afwateringseenheid_code']
    afwateringsgebied_pg_code = config['afwateringseenheden']['kolomnaam_peilgebied_code']

    reference_scenario_name = reference_scenario_config['scenario']['naam']
    scenario_name = scenario_config['scenario']['naam']

    output_folder = os.path.join(base_path, config['output']['folder_pad'])
    output_prefix = config['output']['prefix']

    # Script --------------------------------------------
    afw = gpd.read_file(fn_afwateringsgebied)
    print(f"Het ingelezen bestand heeft de volgende kolommen: {list(afw.columns)}")


    ########################################################


    mapping_columns = {
        'AFWEENHEID': afwateringsgebied_code,
        'PEILGEBIED': afwateringsgebied_pg_code,
        'PG_AGR': '',
        'POLDER_ADM': '',
        'POLDER': '',
        'GEM_CAP': '',
        'JAAR': '',
        'KLIMAATSCE': '',
        'INITPEIL': '',
        'WINTERPEIL': 'WS_LAAGPEI',
        'ZOMERPEIL': 'WS_HOOGPEI',
        'Bemalen': '',
        'AANGEPAST': '',
        'OPMERKING': '',
        'T10TOETS': '',
        'T10TOE_AFW': '',
        'T10HUIDIG': '',
        'T10TOEKOM': '',
        'T25TOETS': '',
        'T25TOE_AFW': '',
        'T25HUIDIG': '',
        'T25TOEKOM': '',
        'T50TOETS': '',
        'T50TOE_AFW': '',
        'T50HUIDIG': '',
        'T50TOEKOM': '',
        'T100TOETS': '',
        'T100TOE_AF': '',
        'T100HUIDIG': '',
        'T100TOEKOM': '',
        }


    # Script -----------------------------------------------------------
    # Maak een lege watersteutel aan
    watersleutel = gpd.GeoDataFrame(columns=list(mapping_columns.keys()))

    # Voeg de kolommen en geometry van de afwateringsgebieden toe aan de watersleutel
    for key, value in mapping_columns.items():
        if value in afw.columns:
            watersleutel.loc[:,key] = afw[value]

    # Set index en voeg geometrie toe op basis van de index
    afw = afw.set_index(mapping_columns['AFWEENHEID'], drop=False)
    watersleutel = gpd.GeoDataFrame(watersleutel.set_index('AFWEENHEID', drop=False))
    watersleutel["geometry"] = afw.geometry
    watersleutel.head()


    ######################################################


    fn_huidig = f"{output_folder}/Knelpunten_{reference_scenario_name}/statistiek/{output_prefix}waterstandsstatistiek_{reference_scenario_name}.shp" # bestandsnaam basisbestand
    kolom_id_huidig = "index" # kolom met unieke ID die correspondeert met het basisbestand

    # Kolom Watersleutel : kolom inladen data
    kolom_mapping = {"T10HUIDIG": "T10",
                    "T25HUIDIG": "T25",
                    "T50HUIDIG": "T50",
                    "T100HUIDIG": "T100",
                    }

    # Script---------------------------------------------------------
    gdf_huidig = gpd.read_file(fn_huidig)
    gdf_huidig.set_index(kolom_id_huidig, inplace=True)

    #Set the T10 column to the minimum value of T10 and T10_GROEI
    gdf_huidig['T10'] = gdf_huidig[['T10', 'T10_GROEI']].min(axis=1, skipna=True)
    watersleutel[list(kolom_mapping.keys())] = gdf_huidig.loc[:,list(kolom_mapping.values())]
    watersleutel[list(kolom_mapping.keys())].head()



    ##################################################


    fn_toekomst = f"{output_folder}/Knelpunten_{scenario_name}/statistiek/{output_prefix}waterstandsstatistiek_{scenario_name}.shp"# bestandsnaam met resultaten
    kolom_id_toekomst = "index" # kolom met unieke ID die correspondeert met het basisbestand
    # Kolom Watersleutel : kolom inladen data
    kolom_mapping_toekomst = {"T10TOEKOM": "T10",
                    "T25TOEKOM": "T25",
                    "T50TOEKOM": "T50",
                    "T100TOEKOM": "T100",
                    }

    # Script ----------------------------------------------
    gdf_toekomst = gpd.read_file(fn_toekomst)
    gdf_toekomst.set_index(kolom_id_toekomst, inplace=True)
    gdf_toekomst['T10'] = gdf_toekomst[['T10', 'T10_GROEI']].min(axis=1, skipna=True)

    watersleutel[list(kolom_mapping_toekomst.keys())] = gdf_toekomst.loc[:,list(kolom_mapping_toekomst.values())]
    watersleutel[list(kolom_mapping_toekomst.keys())].head()


    ##################################################

    watersleutel.loc[:,"KLIMAATSCE"]="KNMI 2019/+ 2050 WLC_H"
    watersleutel.head()


    ###############################################


    fn_toets_pg = f"{output_folder}/Toetsing/{output_prefix}Toetshoogte_peilgebieden.shp" # bestandsnaam met toetsresultaten
    kolom_id_peilgebied = "CODE" # kolom met unieke ID die correspondeert met het basisbestand

    kolom_mapping_toets = {"T10TOETS": "T10",
                    "T25TOETS": "T25",
                    "T50TOETS": "T50",
                    "T100TOETS": "T100",
                    }

    # Script---------------------------------------------------------
    gdf_toets = gpd.read_file(fn_toets_pg)
    gdf_toets.set_index(kolom_id_peilgebied, inplace=True)
    for txwl, tx in kolom_mapping_toets.items():
        watersleutel[txwl] = watersleutel.apply(lambda x: gdf_toets.loc[x["PEILGEBIED"], tx], axis=1)
    gdf_toets.head()


    #####################################################

    fn_toets_afw = f"{output_folder}/Toetsing/{output_prefix}Toetshoogte_afwateringseenheden.shp" # bestandsnaam met toetsresultaten
    kolom_id_afw = "CODE" # kolom met unieke ID die correspondeert met het basisbestand

    kolom_mapping_toets_afw = {"T10TOE_AFW": "T10",
                    "T25TOE_AFW": "T25",
                    "T50TOE_AFW": "T50",
                    "T100TOE_AF": "T100",
                    }

    # Script---------------------------------------------------------
    gdf_toets_afw = gpd.read_file(fn_toets_afw)
    gdf_toets_afw.set_index(kolom_id_afw, inplace=True)
    # Replace the T10 column with the minimum value of T10 and T10_GROEI (ignore nodata)
    gdf_toets_afw['T10'] = gdf_toets_afw[['T10', 'T10_GROEI']].replace(-999,np.NaN).min(axis=1, skipna=True)


    watersleutel[list(kolom_mapping_toets_afw.keys())] = gdf_toets_afw.loc[:,list(kolom_mapping_toets_afw.values())]
    watersleutel[list(kolom_mapping_toets_afw.keys())].head()


    ###############################################

    fn_output = r"watersleutel" # naam van het uitvoerbestand (zonder extentie)

    # Script---------------------------------------------------------

    output = os.path.join(output_folder, fn_output+".shp")
    watersleutel[list(mapping_columns.keys())+["geometry"]].reset_index(drop=True).to_file(output)
    print(f"Het bestand is weggeschreven naar: {output}")

if __name__ == "__main__":
    main()