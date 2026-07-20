import sys
import os.path


def test_path(filepath: str, role: str) -> str:
    """Tests whether the file exists for input files (function, prompts)"""
    if not os.path.isfile(filepath):
        raise ValueError(f"The file for {role} does not exist: {filepath}")
    return filepath


def test_path_output(filepath: str, role: str) -> str:
    """Test the output file, and creates it if doesn't exist"""
    if not os.path.isfile(filepath):
        print(f"The file for {role} does not exist: {filepath}, creating...")
        with open(filepath, 'w') as _:
            ...
        print(f"{filepath} created.")
    return filepath


def flag_parser(args: list) -> tuple[str, str, str]:
    """Set default files for input and output, then checks if they
    are being overriden by the way we called our program"""
    input_path, output_path, functions_definition_path = (
        './data/input/function_calling_tests.json',
        './data/output/function_calling_results.json',
        './data/input/functions_definition.json')

    values_set = {'i': 0, 'f': 0, 'o': 0}

    try:
        for i, arg in enumerate(args[1:]):
            if arg == '--input' or arg == '-i' and values_set['i'] == 0:
                input_path = args[i + 2]
                test_path(input_path, "prompts")
                values_set['i'] = 1
            elif (arg == '--output' or arg == '-o') and values_set['o'] == 0:
                output_path = args[i + 2]
                test_path_output(output_path, 'output file')
                values_set['o'] = 1
            elif arg == '--functions_definitions' or arg == '-f' \
                    and values_set['f'] == 0:
                functions_definition_path = args[i + 2]
                test_path(functions_definition_path, 'functions definitions')
                values_set['f'] = 1
            elif args[i] in ['-i', '-o', '-f', '--input', '--output',
                             '--functions_definitions'] or i == len(args) - 2:
                pass
            else:
                print("This flag does not exist", arg)
    except ValueError as e:
        print("Error when parsing an argument file :", e)
    except IndexError:
        print("Index error : A flag cannot be the last argument")

    return input_path, output_path, functions_definition_path


if __name__ == '__main__':
    flag_parser(sys.argv)
