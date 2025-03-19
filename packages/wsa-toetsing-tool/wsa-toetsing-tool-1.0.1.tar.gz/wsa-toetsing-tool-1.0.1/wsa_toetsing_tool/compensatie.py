from pathlib import Path
import geopandas as gpd
import numpy as np

from wsa_toetsing_tool.config import COL_LIST, COL_LIST_SHORT_DICT

def compensatie_naar_toetshoogte(
        output_dir,
        prefix_output,
        klimaatscenario = 'huidig',
        volumetoename_code_col = 'CODE',
        toetshoogte_code_col = 'CODE',
        toetshoogte_peil_col = 'peil'
):
    """
    Bepaalt het oppervlak open water wat extra gegraven moet worden binnen een peilgebied om de waterstand van een
    scenario te reduceren tot de toetshoogte.
    """
    # Determine file location
    fn_volumetoename_peilgebied = Path(
        output_dir) / f"Knelpunten_{klimaatscenario}" / "volumetoename" / f"{prefix_output}Volume_boven_toetshoogte_peilgebieden_{klimaatscenario}.shp"
    fn_toetshoogte_peilgebied = Path(output_dir) / "Toetsing" / f"{prefix_output}Toetshoogte_peilgebieden.shp"

    # Read files
    gdf_volumetoename = gpd.read_file(fn_volumetoename_peilgebied)
    gdf_toetshoogte = gpd.read_file(fn_toetshoogte_peilgebied)

    # Set index
    gdf_volumetoename = gdf_volumetoename.set_index(volumetoename_code_col)
    gdf_toetshoogte = gdf_toetshoogte.set_index(toetshoogte_code_col)

    # Rename to code (in case it isn't already)
    gdf_volumetoename.index = gdf_volumetoename.index.rename('CODE')
    gdf_toetshoogte.index = gdf_toetshoogte.index.rename('CODE')

    # Merge data
    gdf_compensatie = gpd.GeoDataFrame(gdf_toetshoogte[[toetshoogte_peil_col] + COL_LIST].merge \
                                           (gdf_volumetoename, on='CODE', suffixes=('_TH', '_dV')))

    # Set -999 to np.nan
    gdf_compensatie = gdf_compensatie.replace(-999, np.NaN)

    for Tx in COL_LIST:
        gdf_compensatie[f"{Tx}_dH"] = gdf_compensatie[f"{Tx}_TH"] - gdf_compensatie[toetshoogte_peil_col]

    for Tx in COL_LIST:
        gdf_compensatie[f"{Tx}_dAow"] = gdf_compensatie[f"{Tx}_dV"] / gdf_compensatie[f"{Tx}_dH"]

    # set np.nan back to -999
    gdf_compensatie = gdf_compensatie.replace(np.NaN, -999)

    # Rename columns
    gdf_compensatie = gdf_compensatie.rename(
        columns={
            "T10_GROEI_TH": "T10G_TH",
            "T10_GROEI_dH": "T10G_dH",
            "T10_GROEI_dV": "T10G_dV",
            "T10_GROEI_dAow": "T10G_dAow"
        }
    )

    # Reorder columns
    gdf_compensatie = gdf_compensatie[
        ['peil', 'T10_TH', 'T10_dH', 'T10_dV', 'T10_dAow', 'T10G_TH', 'T10G_dH', 'T10G_dV', 'T10G_dAow', 'T25_TH',
         'T25_dH', 'T25_dV', 'T25_dAow', 'T50_TH', 'T50_dH', 'T50_dV', 'T50_dAow', 'T100_TH', 'T100_dH', 'T100_dV',
         'T100_dAow', 'geometry']]

    # Determine output location and create folder
    output_filename = Path(
        output_dir) / f"Knelpunten_{klimaatscenario}" / "compensatie naar toetshoogte" / f"{prefix_output}compensatie_naar_toetshoogte"
    Path.mkdir(output_filename.parent, exist_ok=True, parents=True)

    # Write to shapefile
    gdf_compensatie.to_file(output_filename.with_suffix('.shp'))

    # Write to Excel
    gdf_compensatie.drop(columns=['geometry']).to_excel(output_filename.with_suffix('.xlsx'))

def compensatie_scenarios(
        output_dir,
        prefix_output,
        fn_peilgebieden,
        referentiescenario,
        vergelijkscenario,
        initieel_peil_col='WS_HOOGP_1',
        kae_code_col='CODE',
        kae_pg_code_col='PG_CODE',
        peilgebied_code_col='CODE',
):
    """
    Vergelijkt twee scenario's (bijvoorbeeld huidig en toekomstig) en bepaald de volumetoename en de compensatieopgave
    om de volumetoename binnen de waterstandsstijging te bergen
    """


    # Bepaal invoerbestanden
    fn_volumetoename_afwateringsgebieden = Path(
        output_dir) / f"Knelpunten_{vergelijkscenario}" / "volumetoename" / f"{prefix_output}Volumetoename_afwateringsgebieden_{vergelijkscenario}.shp"
    fn_volumetoename_afwateringsgebieden_ref = Path(
        output_dir) / f"Knelpunten_{referentiescenario}" / "volumetoename" / f"{prefix_output}Volumetoename_afwateringsgebieden_{referentiescenario}.shp"

    fn_statistiek_afwateringsgebieden = Path(
        output_dir) / f"Knelpunten_{referentiescenario}" / "statistiek" / f"{prefix_output}gebieden_statistiek_{referentiescenario}.shp"

    # Lees invoerbestanden in
    gdf_stat = gpd.read_file(fn_statistiek_afwateringsgebieden)
    gdf_volume = gpd.read_file(fn_volumetoename_afwateringsgebieden).drop(columns=['geometry']).set_index(kae_code_col)
    gdf_volume_ref = gpd.read_file(fn_volumetoename_afwateringsgebieden_ref).drop(columns=['geometry']).set_index(kae_code_col)
    gdf_volume_difference = gdf_volume.subtract(gdf_volume_ref.values)

    # Verwijder niet-gebruikte kolommen
    gdf_stat = gdf_stat.filter([kae_code_col, kae_pg_code_col, initieel_peil_col, 'T10',
                                'T10_GROEI', 'T25', 'T50', 'T100', 'geometry'])

    # Bepaal laagste KAE waterstand per PG en voeg dit toe aan iedere KAE
    # Bepaal laagste KAE-waterstand binnen peilgebied
    gdf_ws_per_peilgebied = gdf_stat[[kae_pg_code_col] + COL_LIST].groupby(kae_pg_code_col).min()
    gdf_stat_min = gdf_stat.drop(columns=COL_LIST).merge(gdf_ws_per_peilgebied, how="left", on=kae_pg_code_col,
                                                         suffixes=(None, None))

    # Voeg bestanden samen op code
    gdf_merge = gdf_stat.merge(gdf_volume_difference, on=kae_code_col, suffixes=("_H", "_dV"))
    gdf_merge_min = gdf_stat_min.merge(gdf_volume_difference, on=kae_code_col, suffixes=("_H", "_dV"))
    # Maak een kopie voor de analyse die gebruik maakt van de kleinste peilsteiging in het peilgebied

    for Tx in COL_LIST:
        # Bepaal waterstandsteiging Tx_dH
        gdf_merge[f"{Tx}_dH"] = gdf_merge[f"{Tx}_H"] - gdf_merge[initieel_peil_col].astype(float)
        gdf_merge_min[f"{Tx}_dH"] = gdf_merge_min[f"{Tx}_H"] - gdf_merge_min[initieel_peil_col].astype(float)
        # TODO: set minimum on 0 so there is no negative water level

    for Tx in COL_LIST:
        gdf_merge[f"{Tx}_dAow"] = gdf_merge[f"{Tx}_dV"] / gdf_merge[f"{Tx}_dH"]
        gdf_merge_min[f"{Tx}_dAow"] = gdf_merge_min[f"{Tx}_dV"] / gdf_merge_min[f"{Tx}_dH"]

    # Verkort de kolomnamen met GROEI voor betere leesbaarheid in shapefile
    gdf_merge = gdf_merge.rename(
        columns={
            "T10_GROEI_H": "T10G_H",
            "T10_GROEI_dH": "T10G_dH",
            "T10_GROEI_dV": "T10G_dV",
            "T10_GROEI_dAow": "T10G_dAow"
        }
    )

    gdf_merge_min = gdf_merge_min.rename(
        columns={
            "T10_GROEI_H": "T10G_H",
            "T10_GROEI_dH": "T10G_dH",
            "T10_GROEI_dV": "T10G_dV",
            "T10_GROEI_dAow": "T10G_dAow"
        }
    )

    # Aggregeer naar peilgebied-niveau
    aggregation_columns = ['T10_dV', 'T10G_dV', 'T25_dV', 'T50_dV', 'T100_dV', 'T10_dAow', 'T10G_dAow', 'T25_dAow',
                           'T50_dAow', 'T100_dAow']
    gdf_peilgebieden = gpd.read_file(fn_peilgebieden)
    gdf_peilgebieden = gdf_peilgebieden.set_index(peilgebied_code_col)
    gdf_merge_aggregated = gdf_merge.groupby(kae_pg_code_col).sum()[aggregation_columns]
    gdf_merge_aggregated_min = gdf_merge_min.groupby(kae_pg_code_col).sum()[aggregation_columns]

    gdf_merge_aggregated = gdf_peilgebieden.join(gdf_merge_aggregated, how='left')
    gdf_merge_aggregated_min = gdf_peilgebieden.join(gdf_merge_aggregated_min, how='left')

    # Bepaal bestandsnamen
    output_filename = Path(output_dir) / "Compensatieopgave" / f"{prefix_output}KAE_compensatieopgave_{vergelijkscenario}_tov_{referentiescenario}"
    output_filename_min = Path(
        output_dir) / "Compensatieopgave" / f"{prefix_output}KAE_compensatieopgave_obv_kleinste_peilstijging_{vergelijkscenario}_tov_{referentiescenario}"

    aggregated_output_filename = Path(
        output_dir) / "Compensatieopgave" / f"{prefix_output}peilgebieden_compensatieopgave_{vergelijkscenario}_tov_{referentiescenario}"
    aggregated_output_filename_min = Path(
        output_dir) / "Compensatieopgave" / f"{prefix_output}peilgebieden_compensatieopgave_obv_kleinste_peilstijging_{vergelijkscenario}_tov_{referentiescenario}"

    # Maak map aan als die nog niet bestaat
    Path.mkdir(output_filename.parent, exist_ok=True, parents=True)

    # Schrijf weg naar shapefile
    gdf_merge.to_file(output_filename.with_suffix('.shp'))
    gdf_merge_min.to_file(output_filename_min.with_suffix('.shp'))

    gdf_merge_aggregated.to_file(aggregated_output_filename.with_suffix('.shp'))
    gdf_merge_aggregated_min.to_file(aggregated_output_filename_min.with_suffix('.shp'))

    # Schrijf weg naar Excel
    gdf_merge.drop(columns=['geometry']).set_index(kae_code_col).to_excel(output_filename.with_suffix('.xlsx'))
    gdf_merge_min.drop(columns=['geometry']).set_index(kae_code_col).to_excel(output_filename_min.with_suffix('.xlsx'))

    gdf_merge_aggregated.drop(columns=['geometry']).to_excel(aggregated_output_filename.with_suffix('.xlsx'))
    gdf_merge_aggregated_min.drop(columns=['geometry']).to_excel(aggregated_output_filename_min.with_suffix('.xlsx'))
