from argparse import ArgumentParser
from shared import Option, Profile, VALID_PROFILE_OPTIONS

def validate_profile_option(line):
    option = Option(line, VALID_PROFILE_OPTIONS)
    return option.is_valid_key() and option.is_valid()

parser = ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filenames', nargs='+', type=Profile)

args = parser.parse_args()

for path in args.filenames:
    class_name, trailing_fragment, _ = path.path_parts()
    file_contents = []

    with open(path) as handle:
        header = True
        for line in handle.readlines():
            line = line.strip()
            if not len(line):
                continue
            if line[0] == '#':
                if header and validate_profile_option(line[1:].strip()):
                    line = line[1:].strip()
            else:
                header = False
            file_contents.append(line)

    for v in file_contents:
        print(v)
