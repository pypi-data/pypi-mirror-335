from wsa_toetsing_tool.compensatie import compensatie_scenarios
import configparser
import os
import argparse

def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description="De compensatie_scenarios bepaalt het verschil in volumetoename tussen twee scenario's")
    parser.add_argument('--settings', type=str, default="example_data/settings.ini", help='Path to the settings file')
    parser.add_argument('--referentiescenario', type=str, default="huidig", help='Name of the reference scenario')
    parser.add_argument('--vergelijkscenario', type=str, default="toekomstig", help='Name of the compared scenario')

    # Parse arguments
    args = parser.parse_args()

    # Use the provided settings file path
    settings = args.settings
    referentiescenario = args.referentiescenario
    vergelijkscenario = args.vergelijkscenario


    base_path = os.path.dirname(settings)
    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(settings)

    # Definieer de locatie waar tussenresultaten gelezen kunnen worden en eindresultaten weggeschreven
    output_dir = os.path.join(base_path, config['output']['folder_pad'])
    prefix_output = config['output']['prefix']
    initieel_peil_col = config['peilgebieden']['kolomnaam_peilgebied_peil_statistiek']
    kae_code_col = config['afwateringseenheden']['kolomnaam_afwateringseenheid_code'] # Kolom in kleinste afwateringseenheden die de code van het afwateringseenheid aangeeft
    kae_pg_code_col = config['afwateringseenheden']['kolomnaam_peilgebied_code'] # Kolom in kleinste afwateringseenheden shapefile die het bijbehorende peilgebied aangeeft
    peilgebied_code_col = config['peilgebieden']['kolomnaam_peilgebied_code'] # Kolom in peilgebieden shapefile die de code van het peilgebied aangeeft

    fn_peilgebieden = os.path.join(base_path, config['peilgebieden']['bestand_pad'])

    compensatie_scenarios(
            output_dir,
            prefix_output,
            fn_peilgebieden,
            referentiescenario,
            vergelijkscenario,
            initieel_peil_col=initieel_peil_col,
            kae_code_col=kae_code_col,
            kae_pg_code_col=kae_pg_code_col,
            peilgebied_code_col=peilgebied_code_col
    )

if __name__ == "__main__":
    main()