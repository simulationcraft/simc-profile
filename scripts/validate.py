from argparse import ArgumentParser
from shared import ParsedOption, Profile, HEADER_OPTIONS, SIMC_OPTIONS

def parse_header_option(line, profile):
    option = ParsedOption(line)

    # only validate header options if they look like they could be options
    if option.validate_key(HEADER_OPTIONS) and not option.validate_value(HEADER_OPTIONS):
        print(f'Profile {profile} has invalid Header option {option}.')

def parse_simc_option(line, profile):
    option = ParsedOption(line)
    if option.validate_class(profile):
        if not option.validate_class_value(profile):
            print(f'Profile {profile} has invalid name {option}. Expected {profile.expected_name()}.')
    elif not option.validate_key(SIMC_OPTIONS):
        print(f'Profile {profile} has invalid Profile option {option.key}.', end='')
        if option.validate_key(HEADER_OPTIONS):
            print(' Perhaps this option was intended to be placed in header?')
        else:
            print()
    elif not option.validate_value(SIMC_OPTIONS):
        print(f'Profile {profile} has invalid Profile option {option}.')

parser = ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filenames', nargs='+', type=Profile)

args = parser.parse_args()

for profile in args.filenames:
    class_name, trailing_fragment, _ = profile.path_parts()

    with open(profile) as handle:
        header = True
        for line in handle.readlines():
            line = line.strip()
            if not len(line):
                continue
            if line[0] == '#':
                if header:
                    parse_header_option(line[1:].strip(), profile)
            else:
                header = False
                parse_simc_option(line, profile)
