from argparse import ArgumentParser
from shared import ParsedOption, Profile, HEADER_OPTIONS, SIMC_OPTIONS

def parse_header_option(line, profile):
    option = ParsedOption(line)

    # only validate header options if they look like they could be options
    if option.validate_key(HEADER_OPTIONS) and not option.validate_value(HEADER_OPTIONS):
        print(f'Profile {profile} has invalid Header option {option}.')
        return False

    return True

def parse_simc_option(line, profile):
    option = ParsedOption(line)
    if option.validate_class(profile):
        if not option.validate_class_value(profile):
            print(f'Profile {profile} has invalid name {option}. Expected {profile.expected_name()}.')
            return False
        return True

    if not option.validate_key(SIMC_OPTIONS):
        print(f'Profile {profile} has invalid Profile option {option.key}.', end='')
        if option.validate_key(HEADER_OPTIONS):
            print(' Perhaps this option was intended to be placed in header?')
        else:
            print()
        return False
    elif not option.validate_value(SIMC_OPTIONS):
        print(f'Profile {profile} has invalid Profile option {option}.')
        return False

    return True

parser = ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filenames', nargs='*', type=Profile)

args = parser.parse_args()

if not len(args.filenames):
    exit(0)

success = True

for profile in args.filenames:
    if not profile.validate():
        print(profile)
        success = False
    class_name, trailing_fragment, _ = profile.path_parts()

    with open(profile) as handle:
        header = True
        for line in handle.readlines():
            line = line.strip()
            if not len(line):
                continue
            if line[0] == '#':
                if header:
                    if not parse_header_option(line[1:].strip(), profile):
                        print(line)
                        success = False
            else:
                header = False
                if not parse_simc_option(line, profile):
                    print(line)
                    success = False

if success:
    exit(0)
else:
    exit(1)
