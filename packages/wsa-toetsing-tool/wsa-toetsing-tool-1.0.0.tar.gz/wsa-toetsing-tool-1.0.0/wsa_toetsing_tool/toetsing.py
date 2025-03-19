import os
import rasterio
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import mapping
from rasterio import fill
from rasterio.mask import mask
from tqdm import tqdm
from scipy import ndimage

from wsa_toetsing_tool.config import T_LABEL_DICT, T_LIST_DICT


def toetsinganalyse(gebied_id: str, geom, drempelhoogte: float, peil: float, path_export: str, watervlakken_raster: str, norm_raster: str, dem_raster: str, panden_raster: str, peilstijgingen: np.array, percentages: list):
    """Uitvoeren van de voor de opgegeven geometrie (shapely polygon). Het waterpeil wordt stapsgewijs opgehoogd om te bepalen hoeveel inundatie er optreed bij de opgegeven percentages.


    Args:
        gebied_id (str): unieke code van het gebied
        geom (shapely polygon): geometry van het gebied
        drempelhoogte (float): drempelhoogte waarmee de panden in het maaiveld raster worden opgehoogd
        peil (float): waterpeil, startpunt van de ophoging
        path_export (str): map waar de resultaten naar worden weggeschreven
        watervlakken_raster (str): watervlakken raster mask 
        norm_raster (str): normeringsraster
        dem_raster (str): hoogteraster
        panden_raster (str): panden raster mask
        peilstijgingen (np.array): numpy array met de peilstijgingen die worden doorgerekend
        percentages (list): inundatiepercentages die worden beschouwd
    """

    pgpad = os.path.join(path_export, gebied_id)
    if not os.path.exists(pgpad):
        os.makedirs(pgpad)

    # Watervlakken
    with rasterio.open(watervlakken_raster) as fw:
        cropped_watervlakken, out_transform = mask(
            fw, shapes=[mapping(geom)], crop=True)
        out_meta = _get_updated_meta(fw, cropped_watervlakken, out_transform)

    with rasterio.open(f'{pgpad}/watervlakken.tif', 'w', **out_meta) as fw:
        fw.write(cropped_watervlakken)

    cropped_watervlakken[cropped_watervlakken == fw.nodata] = 0
    cropped_watervlakken[cropped_watervlakken != 0] = 1
    watervlak = cropped_watervlakken.astype(bool)

    # Normenkaart
    with rasterio.open(norm_raster) as fn:
        cropped_normenkaart, out_transform = mask(
            fn, shapes=[mapping(geom)], crop=True)
        out_meta = _get_updated_meta(fn, cropped_normenkaart, out_transform)

    with rasterio.open(f'{pgpad}/normenkaart.tif', 'w', **out_meta) as fn:
        fn.write(cropped_normenkaart)

    normenkaart = cropped_normenkaart
    normenkaart[normenkaart == fn.nodata] = 0

    # maaiveldhoogte
    with rasterio.open(dem_raster) as fb:
        cropped_bodemhoogte, out_transform = mask(
            fb, shapes=[mapping(geom)], crop=True)
        out_meta = _get_updated_meta(fb, cropped_bodemhoogte, out_transform)

    # panden
    with rasterio.open(panden_raster) as fp:
        cropped_panden, _ = mask(fp, shapes=[mapping(geom)], crop=True)
        cropped_panden[cropped_panden == fp.nodata] = 0

    # Interpoleer de bodemhoogte, waar normenkaart == 100, en bodem == nodata
    # =================
    # Maak een array met nullen op plekken die gevuld moeten worden (alle plekken binnen de rand met nodata)
    fill_mask = ~((cropped_bodemhoogte[0] == fb.nodata) & (
        cropped_normenkaart[0] != fn.nodata))
    # Maak een array met eenen op de plek van de gebouwen, om de drempelhoogte toe te voegen (nodata en pand)
    # building_mask = (cropped_bodemhoogte == fb.nodata) & (cropped_panden == 1)
    building_mask = (cropped_panden == 1)
    # Interpoleer
    cropped_bodemhoogte[cropped_bodemhoogte == fb.nodata] = np.nan
    fill.fillnodata(cropped_bodemhoogte[0], fill_mask.astype(
        int), max_search_distance=100)
    # Verhoog
    cropped_bodemhoogte[building_mask] += drempelhoogte

    # Stel ter plaatse van water de bodemhoogte gelijk aan de waterdiepte
    cropped_bodemhoogte[cropped_watervlakken == 1] = peil

    with rasterio.open(f'{pgpad}/bodemhoogte_toetsing.tif', 'w', **out_meta) as fb:
        fb.write(cropped_bodemhoogte)

    bodemhoogte = cropped_bodemhoogte
    bodemhoogte[(bodemhoogte == fb.nodata) | np.isnan(bodemhoogte)] = 9999.0
    pixeloppervlak = fb.transform.a ** 2
    out_meta = fb.meta.copy()

    # Breidt het watervlak uit met het gebied dat geïnundeerd raakt bij 1 cm peilstijging,
    # En zet de normenkaart voor dit gebied op 0
    inundatie, _ = _bepaal_inundatie(peil + 0.01, bodemhoogte, watervlak)
    watervlak[inundatie] = True
    normenkaart[inundatie] = 0

    # Bepaal de maximum norm in het gebied
    max_norm = np.nanmax(normenkaart)

    inundatiekaart = np.zeros_like(bodemhoogte) * np.nan
    inundatiekaart[watervlak] = 0

    # Bepaal de voorkomende normen in de kaart voor dit peilgebied
    unique_normen, counts = np.unique(
        normenkaart[~np.isnan(normenkaart)], return_counts=True)
    # Filter norm = 0, en tel het aantal pixels per norm
    counts = counts[unique_normen >= 0]
    unique_normen = unique_normen[unique_normen >= 0]
    counts = {norm: cnt for norm, cnt in zip(unique_normen, counts)}

    # Maak een dataframe om de inundaties op te slaan
    translation_dict = T_LABEL_DICT
    column_names = [T_LABEL_DICT[norm] for norm in unique_normen]

    inundatie_df = pd.DataFrame(columns=column_names, index=peilstijgingen)
    inundatie_df.index.name = 'peilstijging'

    volume_gebied = []
    # Verhoog stapsgewijs het peil
    for peilstijging in peilstijgingen:

        # Bepaal waterdiepte
        waterstand = peil + peilstijging

        # Bereken geinundeerd oppervlak
        inundatie, waterdiepte = _bepaal_inundatie(
            waterstand, bodemhoogte, watervlak)
        inundatie[watervlak] = False

        # Bereken inundatievolume
        # volumes.at[np.float32(peilstijging), gebied_id] = waterdiepte.sum() * pixeloppervlak
        volume_gebied.append(float(waterdiepte.sum() * pixeloppervlak))

        # Bepaal het percentage ondergelopen gebied per norm
        for norm, cnt in zip(*np.unique(normenkaart[inundatie], return_counts=True)):
            # if norm == 0.0:
            #     continue
            inundatie_df.at[peilstijging, translation_dict[norm]] = cnt / counts[norm]

    # Sla het inundatie dataframe op
    inundatie_df.reset_index().astype(np.float32).round(4).to_csv(
        f'{pgpad}/peilstijging.csv', sep=',', index=False)

    # Sla het volume dataframe op
    vol_df = pd.DataFrame(
        data={gebied_id: volume_gebied}, index=peilstijgingen)
    vol_df.index.name = 'peilstijging'
    vol_df.reset_index().astype(np.float32).round(4).to_csv(
        f'{pgpad}/volumes.csv', sep=',', index=False)

    # Sla figuur met bergingscurve op
    fig = _plot_bergingscurve(inundatie_df, gebied_id)
    fig.savefig(f'{pgpad}/bergingscurves.png', dpi=220)
    plt.close(fig)

    fn_inundation_percentage_rasters = {}

    for norm, pinundatie in inundatie_df.items():
        # Interpoleer de peilstijging bij het percentage
        peilstijging_bij_p = np.interp(
            percentages, pinundatie.fillna(0.0) * 100, pinundatie.index.values)

        # Maak een lege array om de percentages op te slaan
        percentagekaart = np.zeros_like(watervlak, dtype=np.uint8)

        # Loop door de verschillende niveaus. Doe dit van hoge percentages naar lage
        # zodat de lagere waarden niet overschreven worden door hogere
        for peilstijging, p in zip(peilstijging_bij_p[::-1], percentages[::-1]):
            # Bepaal waterdiepte
            waterstand = peil + peilstijging

            # Bereken geinundeerd oppervlak
            inundatie, waterdiepte = _bepaal_inundatie(
                waterstand, bodemhoogte, watervlak)
            inundatie[watervlak] = False
            # Zet het gebiedsdeel met inundatie en waar de norm geldt op het percentage
            percentagekaart[inundatie & (normenkaart == T_LIST_DICT[norm])] = p

        # Sla kaart op
        out_meta['dtype'] = 'uint8'
        out_meta['nodata'] = 0
        filename = f'{pgpad}/inundatie_percentage_T{int(T_LIST_DICT[norm]):04d}.tif'
        with rasterio.open(filename, 'w', **out_meta) as fp:
            fp.write(percentagekaart)

        fn_inundation_percentage_rasters[norm] = filename

    return fn_inundation_percentage_rasters


def tabel_toetsingsanalyse(percentages: list, gebieden, path_export: str, peilstijgingen: np.array, fn_naam: str = "Samenvatting toetsing", Tx_percentage_toetshoogte={10: 5, 11: 10, 25: 1, 50: 1, 100: 0.1}):
    """De resultaten van de toetsing worden samengevoegd in 1 tabel

    Args:
        percentages (list): Percentages waarvoor de waterstand wordt bepaald
        gebieden (geopandas dataframe): geodataframe met gebieden (peil of afwateringsgebieden)
        path_export (string): Export path
        fn_naam (str): Naam 
        Tx_percentage_toetshoogte (dict): Maximaal toegestaan inundatiepercentage voor bepaling toetshoogte, opgegeven per terugkeertijd. Default: {10: 5, 11: 10, 25: 1, 50: 1, 100: 0.1}

    Returns:
        str: bestandsnaam samenvattende tabel
    """
    tabelwaarden = [
        i/100 for i in sorted(set(percentages + list(range(10, 101, 10))))]

    table_vals = {}

    # Tabel volumes voorbereiden
    volumes = pd.DataFrame(index=peilstijgingen)
    volumes.index = np.round(volumes.index, 2)
    volumes.index.name = "peilstijgingen"

    for idx, peilgebied in tqdm(gebieden.iterrows(), total=len(gebieden), desc='Samenvattende tabel'):
        # Laad rasters in, watervlakken
        pgpad = f'{path_export}/{idx}'

        # Lees dataframe in
        inundatie_df = pd.read_csv(
            f'{pgpad}/peilstijging.csv', sep=',', index_col=0).fillna(0.0)

        # Interpoleer waarden
        for norm, colvalues in inundatie_df.items():
            # Interpoleer de waarden
            pstijg = np.interp(tabelwaarden, colvalues.values,
                               colvalues.index.values)
            table_vals[(idx, norm)] = pstijg

        # Lees volume dataframe in
        volumes[idx] = pd.read_csv(
            f'{pgpad}/volumes.csv', sep=',', index_col=0).fillna(0.0)

    df = pd.DataFrame.from_dict(table_vals, orient='columns')
    df.index = [i*100 for i in tabelwaarden]
    df.index.name = 'Inundatie [%]'
    fn_export = f'{path_export}/{fn_naam}.xlsx'
    writer = pd.ExcelWriter(fn_export)
    df.to_excel(writer, sheet_name='peilstijgingen')
    volumes.astype(np.float32).to_excel(writer, sheet_name='volumes')
    writer.close()

    _toevoegen_toetsingshoogte_aan_shp(
        gebieden, df_peilstijging=df, export_path=path_export, export_name=fn_naam, Tx_perc=Tx_percentage_toetshoogte, peil_column='peil')

    return fn_export


def _toevoegen_toetsingshoogte_aan_shp(gebied_gdf, df_peilstijging, export_path, export_name="toetshoogte_peilgebieden",
                                       Tx_perc: dict = {}, nodata_value=-999.0, peil_column='peil'):
    """Toetsingshoogte toevoegen aan shape met peilgebieden/afwateringseenheden

    Args:
        gebied_gdf (dataframe): peilgebieden/afwateringseenheden
        peil_column (str, optional): Kolom met streefpeil, om de toetingsdiepte bij op te tellen.
        df_peilstijging (_type_): dataframe met peilstijging (uit tabel_toetsingsanalyse())
        export_path (_type_): output map
        export_name (str, optional): bestandsnaam. Defaults to "toetshoogte_peilgebieden".
        Tx_perc (dict): maximaal inundatiepercentage per terugkeertijd. Defaults to {}.
        nodata_value (int, optional): Nodata value wanneer geen norm beschikbaar. Defaults to -999.

    Returns:
        _type_: _description_
    """
    gebied_gdf["index_copy"] = gebied_gdf.index.values
    for tx, tx_perc in Tx_perc.items():
        gebied_gdf[T_LABEL_DICT[tx]] = gebied_gdf.apply(lambda x: _peil_bij_inundatie(
            df_peilstijging.loc[:, x["index_copy"]], x[peil_column], tx=tx, inundatie_percentage=tx_perc, nodata=nodata_value), axis=1)



    fn_output = os.path.join(export_path, export_name+".shp")
    gebied_gdf.to_file(fn_output)
    return fn_output


def _peil_bij_inundatie(df, peil,  tx: int, inundatie_percentage: float, nodata=-999):
    """Waterstand voor het toegestande inundatiepercentage

    Args:
        df (_type_): dataframe met inundatiepercentage, peilen als index en terugkeertijd als kolom
        tx (int): terugkeertijd waarvoor het peil bepaald moet worden
        inundatie_percentage (float): inundatiepercentage waarvoor het peil bepaald moet worden

    Returns:
        float: Waterstand
    """

    #df.columns = df.columns.astype(float).astype(int)
    if T_LABEL_DICT[tx] in df.columns:
        return float(np.interp(inundatie_percentage, df.index, df.loc[:, T_LABEL_DICT[tx]]))+peil
    else:
        return nodata


def _get_updated_meta(f, out_img, out_transform):
    """Update meta data van transformed raster

    Args:
        f (rasterio object): Source 
        out_img (numpy array): new/transformed raster image
        out_transform (dict): new/transformed raster transform

    Returns:
        dict: meta data transformed raster
    """
    out_meta = f.meta.copy()
    out_meta['transform'] = out_transform
    out_meta['compress'] = 'lzw'
    out_meta['height'] = out_img.shape[1]
    out_meta['width'] = out_img.shape[2]
    out_meta['crs'] = {'init': 'epsg:28992'}

    return out_meta


def _plot_bergingscurve(inundatie_df, id):
    """Figuur bergingscurve

    Args:
        inundatie_df (pandas dataframe): dataframe met norm als index.
        id (str): unieke id/code gebied

    Returns:
        _type_: matplotlib fig
    """
    # Functie om bergingscurve te plotten
    fig, ax = plt.subplots()
    for norm, pinundatie in inundatie_df.items():
        ax.plot(pinundatie.values * 100, pinundatie.index,
                label=f'T = {int(round(T_LIST_DICT[norm]))}')

    ax.grid()
    for loc in ['top', 'right']:
        ax.spines[loc].set_visible(False)

    ax.set_ylim(0, 2)
    ax.set_xlim(0, 100.5)
    ax.set_xlabel('Ondergelopen gebied [%]')
    ax.set_ylabel('Peilstijging [m]')

    ax.set_title(id, fontweight='bold')
    ax.legend()

    return fig


def _bepaal_inundatie(waterstand, bodemhoogte, watervlak):
    """
    Functie om inundatie te bepalen op basis van de volgende stappen.
    1. Bepaal de potentiele waterdiepte door de bodemhoogte van de waterstand af te trekken.
    2. Label de watervlakken
    3. Bepaal welke labels kruisen met het watervlakmasker, dit is de inundatie.
    """
    # Bepaal waterdiepte
    waterdiepte = np.maximum(waterstand - bodemhoogte, 0)

    # Label en bepaal het deel dat verbonden in met het watervlak
    labeled, nr = ndimage.label((waterdiepte > 0.0).astype(int))
    geraakt = np.unique(labeled[watervlak])
    inundatie = np.isin(labeled, geraakt)

    return inundatie, waterdiepte
