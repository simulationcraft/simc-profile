from argparse import ArgumentParser
from shared import Option, Profile, VALID_PROFILE_OPTIONS, VALID_SIMC_OPTIONS

def parse_profile_option(line):
    option = Option(line, VALID_PROFILE_OPTIONS)
    if not option.is_valid_key():
        print(f'Profile {path} has invalid Profile option {option.key}.')
    elif not option.is_valid():
        print(f'Profile {path} has invalid Profile option {option}.')

def parse_simc_option(line, class_name, trailing_fragment):
    option = Option(line, VALID_SIMC_OPTIONS)
    if option.key == class_name:
        if not option.is_class(class_name, trailing_fragment):
            print(f'Profile {path} has invalid name {option}. Expected {option.expected_name(class_name, trailing_fragment)}.')
        return
    if not option.is_valid_key():
        print(f'Profile {path} has invalid SimulationCraft option {option.key}.')
    elif not option.is_valid():
        print(f'Profile {path} has invalid SimulationCraft option {option}.')

parser = ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filenames', nargs='+', type=Profile)

args = parser.parse_args()

for path in args.filenames:
    class_name, trailing_fragment, _ = path.path_parts()

    with open(path) as handle:
        header = True
        for line in handle.readlines():
            line = line.strip()
            if not len(line):
                continue
            if line[0] == '#':
                if header:
                    parse_profile_option(line[1:].strip())
            else:
                header = False
                parse_simc_option(line, class_name, trailing_fragment)
