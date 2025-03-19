#!/usr/bin/env python
# coding: utf-8
import os
import tqdm
import rasterio
import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np
import wsa_toetsing_tool.hkvsobekpy_wsa as hkv
from shapely.geometry import box
from rasterio.features import shapes
from scipy import ndimage
from pathlib import Path
from rasterstats import zonal_stats

from wsa_toetsing_tool.helpers import realign_raster_to_reference, add_geometry_to_df
from wsa_toetsing_tool.config import T_LIST_DICT, COL_LIST,  T_GUMBEL, COL_KNELPUNTEN_SHP, \
    COL_KNELPUNTEN_NORM_COL, MAAIVELD_CRITERIUM, COL_LIST_STAT

def waterstandstatistiek(max_wl_df, network, par: str = 'Waterlevel max. (m AD)',
                         period_growingseason=[(3, 1), (10, 1)], venster_array=[0, 10], Ggi=0.44, GgN=0.12, TOI=10, plots=True, export_folder_plot="", n_jaren_plotposities=None, modelpakket='sobek'):
    """
         Args:
            his_df
            network
            period_growingseason (list, optional): format: [(mm, dd), (mm, dd)] - periode voor filtering groeiseizoen. Defaults to [ (3, 1), (10, 1)].
            par (str, optional): parameter in calcpnt.his waarop de statistiek wordt uitgevoerd. Defaults to 'Waterlevel max. (m AD)'.
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
            plots (bool, optional): _description_. Defaults to True.
            n_jaren_plotposities (int, optional): Definieer het aantal gumbel plotposities (aantal jaren waarvoor de reeks representatief is). Als hier geen aantal is opgegeven wordt dit aantal automatisch afgeleid van de tijdreeks

    """

    df_gumbel = pd.DataFrame(columns=COL_LIST_STAT)

    # Bereken aantal gumbel posities als dit niet is opgegeven
    if n_jaren_plotposities is None:
        n_jaren_plotposities = max_wl_df.index.max().year - max_wl_df.index.min().year + 1

    if par not in list(max_wl_df.columns.unique(0)):
        raise ValueError(
            f"{par} komt niet voor in de calcpnt.his kolommen {str(list(max_wl_df.columns.unique(0)))}. Verbeter de input variabele 'calcpnt_par_statistiek'.")

    loc = max_wl_df.columns.get_level_values(1)

    for i in tqdm.tqdm(range(len(max_wl_df.columns.get_level_values(1))), desc='Voortgang afleiden Gumbel statistiek'):
        #Select timeserie and clean nodata and NaT
        ts = max_wl_df.loc[:, [(par, loc[i])]].dropna()
        ts = ts[pd.notna(ts.index)]

        # Skip this datapoint if the ts is empty
        if ts.empty:
            continue

        try:
            ws = hkv.waterlevelstat.AfleidingParameters(
                df_enkel=ts,
                N=n_jaren_plotposities,  # aantal jaren voor bepaling van de plotposities
                vensterArray=venster_array,  # mee te nemen gebeurtenissen
                GumbelT=T_GUMBEL,  # terugkeertijden voor Gumbel functie
                TOI=TOI,  # terugkeertijd voor het gewogen gemiddelde
                startMMdd=period_growingseason[0],  # start groeiseizoen
                endMMdd=period_growingseason[1],  # einde groeseizoen
                jaarmax_as='date',
                Ggi=Ggi,
                GgN=GgN)
        except IndexError:
            raise IndexError(f"Unable to determine waterlevel statistics for point {loc[i]}")

        df_gumbel = pd.concat([df_gumbel,
                               pd.DataFrame(
                                   {
                                        COL_LIST_STAT[0]: ws.stats.stap3.WSarray_TOI_jaar, #T10
                                        COL_LIST_STAT[1]: ws.stats.stap4.WSarray_TOI_jaar, #T10_Groei
                                        COL_LIST_STAT[2]: ws.stats.stap1.GumbelWS[1], #T25
                                        COL_LIST_STAT[3]: ws.stats.stap1.GumbelWS[2],
                                        COL_LIST_STAT[4]: ws.stats.stap1.GumbelWS[3], #T50
                                        COL_LIST_STAT[5]: ws.stats.stap1.GumbelWS[4] #T100
                                   },
                                   index=[loc[i]])])

        if plots == True:
            export_path_png = os.path.join(export_folder_plot, "png")
            if not os.path.exists(export_path_png):
                os.makedirs(export_path_png)
            hkv.waterlevelstat.PlotFiguur(ws, export_folder_plot)

    return add_geometry_to_df(df_gumbel, network[["geometry"]])


def statistiek_per_gebied(gdf_gebieden, gdf_waterstanden, par="mean", additional_pars=[]):
    set1 = set(COL_LIST_STAT)
    set2 = set(list(gdf_waterstanden.columns))
    if not len(set1.intersection(set2)) == len(set1):
        raise ValueError(f"Kolommen {COL_LIST_STAT} niet in waterstandsstatistiek ")

    # Populae parameter with suffix dictionary
    par_list = [par] + additional_pars
    par_suffix_list = [''] + [f'_{par}' for par in additional_pars]

    for Tx in COL_LIST_STAT:
        for parameter, suffix in zip(par_list, par_suffix_list):
            if parameter == "mean":
                gdf_gebieden[Tx + suffix] = gdf_gebieden.apply(
                    lambda x: gdf_waterstanden[gdf_waterstanden.geometry.within(x["geometry"])].loc[:, Tx].mean(), axis=1)
            if parameter == "median":
                gdf_gebieden[Tx + suffix] = gdf_gebieden.apply(
                    lambda x: gdf_waterstanden[gdf_waterstanden.geometry.within(x["geometry"])].loc[:, Tx].median(), axis=1)
            if parameter == "max":
                gdf_gebieden[Tx + suffix] = gdf_gebieden.apply(
                    lambda x: gdf_waterstanden[gdf_waterstanden.geometry.within(x["geometry"])].loc[:, Tx].max(), axis=1)
            if parameter == "min":
                gdf_gebieden[Tx + suffix] = gdf_gebieden.apply(
                    lambda x: gdf_waterstanden[gdf_waterstanden.geometry.within(x["geometry"])].loc[:, Tx].min(), axis=1)

    return gdf_gebieden


def waterdiepte_per_normgebied(fn_normraster: str, fn_dieptegrid: str, fn_output: str, t_norm: int):
    with rasterio.open(fn_dieptegrid) as em:
        data = em.read(1)

    rst_norm, profile_norm = realign_raster_to_reference(
        fn_dieptegrid, fn_normraster)
    normen_raster = xr.where(rst_norm == t_norm, data, np.nan)

    with rasterio.open(fn_output, 'w', **profile_norm) as out:
        out.write(normen_raster, 1)

    return fn_output


def maak_knelpunten_shape(knelpuntrasters: dict, fn_peilgebieden: str, fn_normering: str, path_output, output_prefix="",
                          wsa_titel="", klimaatscenario="", pg_code='CODE'):
    _fn_knelpunten_shp = {}
    knelpunten_merged = gpd.GeoDataFrame(columns=list(COL_KNELPUNTEN_SHP.values()) + ['dummy_geom'], geometry='dummy_geom', crs='EPSG:28992')
    for tx, fn_waterdieptegrid_tx in knelpuntrasters.items():
        mask = None
        with rasterio.Env():
            with rasterio.open(knelpuntrasters[tx]) as src:
                image = src.read(1)  # first band
                image[image > 0] = 1
                image[image != 1] = 0
                results = (
                    {'properties': {'raster_val': v}, 'geometry': s}
                    for i, (s, v)
                    in enumerate(
                        shapes(image, mask=mask, transform=src.transform)))

        geoms = list(results)
        gpd_polygonized_raster = gpd.GeoDataFrame.from_features(geoms)
        gpd_polygonized_raster.set_crs(epsg=src.crs.to_epsg(), inplace=True)
        if len(gpd_polygonized_raster[gpd_polygonized_raster["raster_val"] == 1]) != 0:
            # _fn_knelpunten_shp[tx] = os.path.join(
            #     path_output, f"{output_prefix}knelpunten_{tx}.shp")
            gdf = gpd_polygonized_raster[gpd_polygonized_raster["raster_val"] == 1]
            gdf.loc[:,COL_KNELPUNTEN_SHP["normering"]] = tx
            knelpunten_merged.set_crs(crs="EPSG:28992", inplace=True)
            gdf.set_crs(crs="EPSG:28992", inplace=True)
            knelpunten_merged = gpd.GeoDataFrame(pd.concat([knelpunten_merged, gdf], ignore_index=True).set_crs("EPSG:28992", inplace=True), crs='EPSG:28992')
        else:
            print(
                f"Geen knelpunten voor {tx}. Geen knelpunten shape geexporteerd")

    # determine klimaatscenario_suffix for writing to shapefile
    if klimaatscenario == "" or klimaatscenario is None:
        klimaatscenario_suffix = ""
    else:
        klimaatscenario_suffix = f"_{klimaatscenario}"

    _fn_knelpunten_shp = os.path.join(path_output, f"knelpunten/{output_prefix}knelpunten{klimaatscenario_suffix}.shp")
    #knelpunten_merged.loc[:,COL_KNELPUNTEN_SHP["klimaatscenario"]] = klimaatscenario
    #knelpunten_merged.loc[:,COL_KNELPUNTEN_SHP["wsa_titel"]] = wsa_titel
    #knelpunten_merged.loc[:,COL_KNELPUNTEN_SHP["knelpuntnummer"]]  = list(range(1, 1 + len(knelpunten_merged)))
    #cols.append("geometry")
    Path(_fn_knelpunten_shp).parent.mkdir(parents=True, exist_ok=True)
    #knelpunten_merged[cols].to_file(_fn_knelpunten_shp)


    # Start filtering
    peilgebieden = gpd.read_file(fn_peilgebieden).to_crs("EPSG:28992")

    cols = []

    with rasterio.open(fn_normering) as src:

        for norm, norm_value in T_LIST_DICT.items():
            if norm == 'T0':
                #Skip T0
                continue

            stats = zonal_stats(peilgebieden, src.read(1), affine=src.transform, stats="count", categorical=True,
                                nodata=src.nodata)
            area = [(stat.get(norm_value, 0) * (src.res[0] * src.res[1])) for stat in stats]

            peilgebieden[f'An_{norm}'] = area
            peilgebieden[f'Ad_{norm}'] = [a * MAAIVELD_CRITERIUM[norm] for a in area]

            cols.append(f'An_{norm}')
            cols.append(f'Ad_{norm}')

    knelpunten_per_normering = knelpunten_merged.dissolve(by=COL_KNELPUNTEN_NORM_COL, as_index=False)[
        [COL_KNELPUNTEN_NORM_COL, 'geometry']]
    knelpunten_per_normering_per_peilgebied = peilgebieden.overlay(
        knelpunten_per_normering, keep_geom_type=True, make_valid=True
    )[[pg_code, COL_KNELPUNTEN_NORM_COL, 'geometry'] + cols]
    knelpunten_per_normering_per_peilgebied['A_knelpunt'] = knelpunten_per_normering_per_peilgebied.geometry.area

    # Stap 2: bepaal of knelpunt groter is dan drempelwaarde
    def check_knelpunt(row):
        normering = row[COL_KNELPUNTEN_NORM_COL]
        drempel_column = f'Ad_{normering}'
        return int(
            row['A_knelpunt'] > row[drempel_column])  # convert to int for easier datamanupulation in Excel later on

    knelpunten_per_normering_per_peilgebied['is_knelpunt'] = knelpunten_per_normering_per_peilgebied.apply(
        check_knelpunt, axis=1)

    knelpunten_per_normering_per_peilgebied.to_file(_fn_knelpunten_shp)
    return _fn_knelpunten_shp

def filter_knelpunten_shape(fn_knelpunten_shp: str, fn_peilgebieden: str, fn_normering: str, fn_export: str,
                            pg_code='CODE'):
    # Stap 1 bepaal knelpunt per normering per peilgebied
    knelpunten = gpd.read_file(fn_knelpunten_shp)
    peilgebieden = gpd.read_file(fn_peilgebieden)
    cols = []

    with rasterio.open(fn_normering) as src:

        for norm, norm_value in T_LIST_DICT.items():
            if norm == 'T0':
                continue

            stats = zonal_stats(peilgebieden, src.read(1), affine=src.transform, stats="count", categorical=True)
            area = [(stat.get(norm_value, 0) * (src.res[0] * src.res[1])) for stat in stats]

            peilgebieden[f'An_{norm}'] = area
            peilgebieden[f'Ad_{norm}'] = [a * MAAIVELD_CRITERIUM[norm] for a in area]

            cols.append(f'An_{norm}')
            cols.append(f'Ad_{norm}')

    knelpunten_per_normering = knelpunten.dissolve(by=COL_KNELPUNTEN_NORM_COL, as_index=False)[[COL_KNELPUNTEN_NORM_COL, 'geometry']]
    knelpunten_per_normering_per_peilgebied = peilgebieden.overlay(
        knelpunten_per_normering, keep_geom_type=True, make_valid=True
    )[[pg_code, COL_KNELPUNTEN_NORM_COL, 'geometry'] + cols]
    knelpunten_per_normering_per_peilgebied['A_knelpunt'] = knelpunten_per_normering_per_peilgebied.geometry.area

    # Stap 2: bepaal of knelpunt groter is dan drempelwaarde
    def check_knelpunt(row):
        normering = row[COL_KNELPUNTEN_NORM_COL]
        drempel_column = f'Ad_{normering}'
        return int(row['A_knelpunt'] > row[drempel_column]) # convert to int for easier datamanupulation in Excel later on

    knelpunten_per_normering_per_peilgebied['is_knelpunt'] = knelpunten_per_normering_per_peilgebied.apply(check_knelpunt, axis=1)

    knelpunten_per_normering_per_peilgebied.to_file(fn_export)
    return knelpunten_per_normering_per_peilgebied

def _mask_inundatie_raakt_watervlak(waterdiepte_rst, bgt_rst):
    """
    Functie om inundatie te bepalen op basis van de volgende stappen.
    1. Bepaal de potentiele waterdiepte door de bodemhoogte van de waterstand af te trekken.
    2. Label de watervlakken
    3. Bepaal welke labels kruisen met het watervlakmasker, dit is de inundatie.
    """

    mask = None
    with rasterio.Env():
        with rasterio.open(waterdiepte_rst) as src:
            with rasterio.open(bgt_rst) as bgt:
                profile = src.profile
                image = src.read(1)  # first band
                image[image > 0] = 1
                image[image != 1] = 0
                image_bgt = bgt.read(1)
                image_bgt[image_bgt > 0] = 1
                image_bgt[image_bgt != 1] = 0

                # Label en bepaal het deel dat verbonden in met het watervlak
                labeled, nr = ndimage.label(image.astype(int))

                geraakt = np.unique(labeled[image_bgt.astype(bool)])
                inundatie = np.isin(labeled, geraakt)
    return inundatie


def waterdiepte_filter_norm(norm_raster, fn_diepte_grids, path_output, output_prefix):
    """
    {'T10': 'C:\\Git\\BH9135_WSA\\playground\\ppsw_output_5\\waterdiepte_T10.tif',
  'T10 GROEISEIZOEN': 'C:\\Git\\BH9135_WSA\\playground\\ppsw_output_5\\waterdiepte_T10 GROEISEIZOEN.tif',
  'T25': 'C:\\Git\\BH9135_WSA\\playground\\ppsw_output_5\\waterdiepte_T25.tif',
  'T50': 'C:\\Git\\BH9135_WSA\\playground\\ppsw_output_5\\waterdiepte_T50.tif',
  'T100': 'C:\\Git\\BH9135_WSA\\playground\\ppsw_output_5\\waterdiepte_T100.tif'}
    """

    _fn_waterdiepte_filter_norm = {}
    for Tx, fn_depth in fn_diepte_grids.items():
        if Tx in COL_LIST:
            _fn_waterdiepte_filter_norm[Tx] = os.path.join(
                path_output, f"{output_prefix}knelpunten_waterdiepte_{Tx}.tif")
            waterdiepte_per_normgebied(
                norm_raster, fn_depth, _fn_waterdiepte_filter_norm[Tx], T_LIST_DICT[Tx])

    return _fn_waterdiepte_filter_norm


def genereer_waterdiepte_raster(fn_waterstand_rst, fn_AHN, filename_output, drempel_diepte=0.01, custom_nodata=-999):
    """
    Maak waterdiepteraster aan de hand van waterstandsrasters en het hoogtemodel
    param: fn_waterstand_rst: Bestandslocatie met waterstand raster
    param: fn_AHN: Bestandslocatie van het hoogtemodel
    param: bestandsnaam waaronder weg te schrijven
    param: drempel_diepte: Minimale waarde voor het diepteraster
    param: custom_nodata: Waarde die omgezet wordt in nodata
    return: bestandsnaam van weggeschreven raster
    """
    with rasterio.open(fn_waterstand_rst, 'r+') as src:  # resultaat van mosaic_raster
        ws = src.read(1)
        result_shape = gpd.GeoSeries([box(*src.bounds)])

    with rasterio.open(fn_AHN, 'r') as src:
        out_meta = src.meta
        AHN_meta = src.meta
        AHN_nodata = AHN_meta['nodata']
        ahn, out_transform = rasterio.mask.mask(
            src, result_shape, crop=True, nodata=AHN_nodata)
        AHN_bounds = src.bounds
        out_meta.update({"driver": "GTiff",
                         "height": ahn.shape[1],
                         "width": ahn.shape[2],
                         "transform": out_transform,
                         "nodata": np.nan})

    a_0 = np.where(ahn == AHN_nodata, np.nan, ahn[0])
    w_0 = np.where(ws == AHN_nodata, np.nan, ws)
    w_0 = np.where(w_0 == custom_nodata, np.nan, w_0)

    overstromingsdiepte = w_0 - a_0[0]
    overstromingsdiepte[overstromingsdiepte <= drempel_diepte] = 0
    overstromingsdiepte = np.where(
        np.isnan(overstromingsdiepte), AHN_nodata, overstromingsdiepte)
    out_meta.update({"nodata": AHN_nodata})

    # wegschrijven
    Path(filename_output).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(filename_output, 'w+', compress='lzw', **out_meta) as ff:
        ff.write(overstromingsdiepte.astype(out_meta['dtype']), 1)

    return filename_output

def genereer_verschil_raster(fn_scenario, fn_reference, filename_output, nodata_to_zero=True, ignore_negative=True):
    """
    Berekend het verschil tussen een 'scenario-raster' en een 'referentie-raster'
    """
    with rasterio.open(fn_scenario, 'r+') as src:  # resultaat van mosaic_raster
        sce_nodata = src.meta['nodata']
        sce = src.read(1)

    with rasterio.open(fn_reference, 'r') as src:
        out_meta = src.meta
        ref_nodata = src.meta['nodata']
        ref = src.read(1)

    if nodata_to_zero:
        # Set all nodata to 0
        ref = np.where(ref == ref_nodata, 0, ref)
        sce = np.where(sce == sce_nodata, 0, sce)
    else:
        ref = np.where(ref == ref_nodata, np.nan, ref)
        sce = np.where(sce == sce_nodata, np.nan, sce)

    # Calculate differene
    difference = sce - ref

    # Set negative values to 0
    if ignore_negative:
        difference[difference <= 0] = 0

    # wegschrijven
    Path(filename_output).parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(filename_output, 'w+', compress='lzw', **out_meta) as ff:
        ff.write(difference.astype(out_meta['dtype']), 1)

    return filename_output



if __name__ == '__main__':
    # fn_normraster = r"c:\Git\BH9135_WSA\playground\input_PPSW\BGT\BGT_NORM_ras.tif"
    # fn_dieptegrid = r"c:\Git\BH9135_WSA\playground\pc_02\pc_gebieden_waterdiepte_T100.tif"
    # fn_hoogtegrid = r"c:\Git\BH9135_WSA\playground\input_PPSW\AHN\AHN4_WSA.tif"
    # fn_output = r"c:\Git\BH9135_WSA\playground\pc_02\test3_t100.tif"
    # waterdiepte_per_normgebied(
    #     fn_normraster, fn_dieptegrid, fn_output=fn_output, t_norm=100)

    fn_knelpunten_shp = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\output\bbo\Knelpunten_huidig\knelpunten\bbo_knelpunten_huidig.shp'
    fn_peilgebieden = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\input\PeilgebiedPraktijk.shp'
    fn_normering = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\output\bbo\Voorbewerkt\normering_aligned.tif'
    export_path = r'D:\DevOps repositories\Waterhuishouding\wsa_toetsing_tool\examples\output\bbo\Knelpunten_huidig\knelpunten'
    filter_knelpunten_shape(fn_knelpunten_shp, fn_peilgebieden, fn_normering, export_path)
