import unittest
import pytest
import geopandas.testing as gpd_testing

import geopandas as gpd
from wsa_toetsing_tool.wsa_delfland.wsa import Toetsing
import configparser
import os


class TestToetsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        This class is executed before any tests are performed. This class goes through the Toetsing-analysis and
        produces the results. Tests methods are performed afterwards and compare the output with previously produced
        output.
        """
        # Settings file
        settings = "data/input/settings.ini"
        input_path = os.path.dirname(settings)

        config = configparser.ConfigParser(inline_comment_prefixes="#")
        config.read(settings)

        # Export path
        output_dir = config['output']['folder_pad']
        prefix_output = config['output'][
            'prefix']  # prefix voor alle output bestanden, mag ook leeg een lege string zijn: ""

        # Normenraster
        fn_normen_rst = os.path.join(input_path, config['normen']['bestand_pad'])

        # Hoogteraster
        fn_hoogtegrid = os.path.join(input_path, config['hoogtemodel']['bestand_pad'])

        # Peilgebieden
        peilgebieden = os.path.join(input_path, config['peilgebieden']['bestand_pad'])
        peilgebieden_col_code = config['peilgebieden']['kolomnaam_peilgebied_code']
        peilgebieden_col_peil = config['peilgebieden']['kolomnaam_peilgebied_peil_toetsing']

        # Afwaterende eenheden - optioneel
        afweenheid_shp = os.path.join(input_path,
                                      config['afwateringseenheden']['bestand_pad'])  # zet op None indien niet toegepast
        afweenheid_col_code = config['afwateringseenheden']['kolomnaam_afwateringseenheid_code']
        afweenheid_col_peilgebiedcode = config['afwateringseenheden']['kolomnaam_peilgebied_code']

        # BGT
        bgt_shp = os.path.join(input_path, config['bgt']['bestand_pad'])
        bgt_col_functie = config['bgt']['kolomnaam_functie']
        bgt_functie_pand = config['bgt']['functie_pand']
        bgt_functie_watervlak = config['bgt']['functie_watervlak']
        bgt_functie_watervlak = bgt_functie_watervlak.split(',')
        bgt_functie_watervlak = [item.strip() for item in bgt_functie_watervlak]

        # Eventuele drempelhoogte om bebouwing op te hogen (zo niet, kies 0)
        drempelhoogte = eval(config['overig']['drempelhoogte_panden'])

        # Percentages die als niveaus worden aangehouden bij uit te voeren kaart
        percentages_str = config['overig']['percentages']
        percentages_list = percentages_str.split(',')
        percentages = [float(item) if '.' in item else int(item) for item in percentages_list]

        # Inundatiepercentages voor bepaling toetshoogtes per terugkeertijd
        toetshoogte_config_items = config.items('percentages_toetshoogte')
        Tx_percentage_toetshoogte = {int(key): float(value) for key, value in toetshoogte_config_items}

        # Sommige afwateringsgebieden overlappen een heel klein beetje met een ander peilgebied, wat is de maximale fractie?
        kae_max_overlap_andere_peilgebieden = eval(config['overig']['kae_max_overlap_andere_peilgebieden'])

        # Controleren input - onderstaande code niet aanpassen
        cls.wsa_toets = Toetsing(fn_hoogtegrid=fn_hoogtegrid, output_dir=output_dir, output_prefix=prefix_output)

        ##################################################

        cls.wsa_toets.inlezen_peilgebieden(peilgebieden_shp=peilgebieden, peilgebieden_col_code=peilgebieden_col_code,
                                       peilgebieden_col_peil=peilgebieden_col_peil)
        cls.wsa_toets.peilgebieden.head()

        ###################################################

        if afweenheid_shp is not None:
            cls.wsa_toets.inlezen_afwateringseenheden(afweenheid_shp=afweenheid_shp,
                                                  afweenheid_col_code=afweenheid_col_code,
                                                  overlap_threshold=kae_max_overlap_andere_peilgebieden)
            cls.wsa_toets.afwateenheid.head()

        ####################################################

        bgt_panden = cls.wsa_toets.genereren_panden_mask(bgt_shp, bgt_col_functie=bgt_col_functie,
                                                     bgt_functie_pand=[bgt_functie_pand])

        ####################################################

        bgt_watervlak = cls.wsa_toets.genereren_watervlakken_mask(bgt_shp, bgt_col_functie=bgt_col_functie,
                                                              bgt_functie_watervlak=bgt_functie_watervlak)

        ####################################################
        fn_normen_rst = cls.wsa_toets.voorbewerken_normenraster(fn_normen_rst)
        ####################################################
        fn_peil, fn_afw = cls.wsa_toets.toetsing_berging(drempelhoogte, percentages, peilgebieden=True,
                                                     afwateringsgebieden=True)

        cls.wsa_toets.peilgebieden.to_feather('data/output/Toetsing/test_Toetshoogte_peilgebieden.feather')
        cls.wsa_toets.afwateenheid.to_feather('data/output/Toetsing/test_Toetshoogte_afwateringseenheden.feather')


        print("Ready initializing the test")

    @pytest.mark.run(order=1)
    def test_peilgebieden(self):
        """
        Compare if the output on Peilgebieden is unaltered. If anything in the toetspeil-method has changed this should
        assert False
        """
        assert_peilgebieden = gpd.read_feather(r'data/assert/Toetsing/test_Toetshoogte_peilgebieden.feather')
        gpd_testing.assert_geodataframe_equal(self.wsa_toets.peilgebieden, assert_peilgebieden)

    @pytest.mark.run(order=2)
    def test_afwateringseenheden(self):
        """
        Compare if the output on Afwateringseenheden is unaltered. If anything in the toetspeil-method has changed this
        should assert False
        """
        assert_afwateenheid = gpd.read_feather(r'data/assert/Toetsing/test_Toetshoogte_afwateringseenheden.feather')
        gpd_testing.assert_geodataframe_equal(self.wsa_toets.afwateenheid, assert_afwateenheid)



if __name__ == '__main__':
    unittest.main()