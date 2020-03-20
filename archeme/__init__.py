import sys
import getopt
from pathlib import Path
from yaml import load, Loader

from archeme.generate import GenerateGraphvizSource
from archeme.merge import MergeMultipleSchemes


def exit_on_wrong_command():
    print('''Usage:

archeme generate [-c <config_file>] -i <input_file> -o <output_file>

or

archeme merge -i <input_file> -o <output_file>
''')

    sys.exit(2)

def entry_point():
    if(len(sys.argv) < 4):
        exit_on_wrong_command()

    action = sys.argv[1]

    if not action == 'generate' and not action == 'merge':
        exit_on_wrong_command()

    config_file_path = None
    input_file_path = None
    output_file_path = None

    try:
        options, arguments = getopt.getopt(sys.argv[2:], 'c:i:o:', ['config', 'input=', 'output='])

    except getopt.GetoptError:
        exit_on_wrong_command()

    for option, argument in options:
        if option in ("-c", "--config"):
            config_file_path = Path(argument).resolve()

        elif option in ("-i", "--input"):
            input_file_path = Path(argument).resolve()

        elif option in ("-o", "--output"):
            output_file_path = Path(argument).resolve()

        else:
            exit_on_wrong_command()

    if not input_file_path or not output_file_path:
        exit_on_wrong_command()

    with open(input_file_path) as input_file:
        input = load(input_file, Loader)

    if action == 'generate':
        if config_file_path:
            with open(config_file_path) as config_file:
                config = load(config_file, Loader)

            input = {**config, **input}

        output = GenerateGraphvizSource().generate_graphviz_source(input)

    if action == 'merge':
        output = MergeMultipleSchemes().merge_multiple_schemes(input)

    with open(output_file_path, 'w', encoding='utf8') as output_file:
        output_file.write(output)
