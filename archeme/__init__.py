import sys
import getopt
from subprocess import run, PIPE, STDOUT, CalledProcessError
from pathlib import Path
from yaml import load, Loader

from archeme.generate import GenerateGraphvizSource
from archeme.merge import MergeMultipleSchemes


def exit_on_wrong_command():
    print('''Usage:

archeme generate [-c|--config <config_file>] -i|--input <input_file> -o|--output <output_file> [-d|--draw <format>]

or

archeme merge -i|--input <input_file> -o|--output <output_file>
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
    draw_format = None

    try:
        options, arguments = getopt.getopt(
            sys.argv[2:],
            'c:i:o:d:',
            ['config=', 'input=', 'output=', 'draw=']
        )

    except getopt.GetoptError:
        exit_on_wrong_command()

    for option, argument in options:
        if option in ('-c', '--config'):
            config_file_path = Path(argument).resolve()

        elif option in ('-i', '--input'):
            input_file_path = Path(argument).resolve()

        elif option in ('-o', '--output'):
            output_file_path = Path(argument).resolve()

        elif option in ('-d', '--draw'):
            draw_format = argument

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

    if action == 'generate' and draw_format:
        draw_engine = input.get('engine', 'dot')

        if draw_engine == 'dot':
            draw_command = f'{draw_engine} '

        elif draw_engine == 'neato' or draw_engine == 'fdp':
            draw_command = f'{draw_engine} -n '

        else:
            print(f'WARNING: the specified engine {draw_engine} is unknown. Only dot, neato, and fdp are supported')

            draw_command = f'{draw_engine} '

        drawing_file_path = output_file_path.parent / f'{output_file_path.stem}.{draw_format}'

        draw_command += f'-T {draw_format} "{output_file_path}" -o "{drawing_file_path}"'

        print(f'Trying to execute the command:\n{draw_command}')

        try:
            command_output = run(draw_command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            if command_output.stdout:
                command_output_decoded = command_output.stdout.decode('utf8', errors='ignore')

                print(command_output_decoded)

        except CalledProcessError as exception:
            print(str(exception))

            sys.exit(1)
