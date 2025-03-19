from wsa_toetsing_tool.compensatie import compensatie_naar_toetshoogte
import configparser
import argparse
import os

def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='De compensatie naar toetshoogte bepaalt het compensatieoppervlak en -volume om de waterstandsstijging te beperken tot aan de toetshoogte')
    parser.add_argument('--settings', type=str, default="example_data/settings.ini", help='Path to the settings file')
    parser.add_argument('--scenario_settings', type=str, default="example_data/settings_huidig.ini", help='Path to the scenario settings file')

    # Parse arguments
    args = parser.parse_args()

    # Use the provided settings file path
    settings = args.settings
    scenario_settings = args.scenario_settings

    config = configparser.ConfigParser(inline_comment_prefixes="#")
    config.read(settings)

    scenario_config = configparser.ConfigParser(inline_comment_prefixes="#")
    scenario_config.read(scenario_settings)

    base_path = os.path.dirname(settings)
    output_dir = os.path.join(base_path, config['output']['folder_pad'])
    prefix_output = config['output']['prefix']
    klimaatscenario = scenario_config['scenario']['naam']

    volumetoename_code_col = config['peilgebieden']['kolomnaam_peilgebied_code']
    toetshoogte_code_col = config['peilgebieden']['kolomnaam_peilgebied_code']
    toetshoogte_peil_col = 'peil'

    compensatie_naar_toetshoogte(
            output_dir,
            prefix_output,
            klimaatscenario,
            volumetoename_code_col,
            toetshoogte_code_col,
            toetshoogte_peil_col
    )

if __name__ == "__main__":
    main()