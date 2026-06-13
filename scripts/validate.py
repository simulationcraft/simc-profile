from argparse import ArgumentParser
from dataclasses import dataclass
from difflib import ndiff
from json import loads
from urllib.request import Request, urlopen

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

def validate(profile: Profile):
    success = True

    if not profile.validate():
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
                        success = False
            else:
                header = False
                if not parse_simc_option(line, profile):
                    success = False
    return success

@dataclass
class Change:
    description: str
    line: int
    old: str
    new: str

    def diff(self):
        def color_line(line: str):
            if line[0] == '-':
                return '\033[31m' + line + '\033[0m'
            if line[0] == '+':
                return '\033[92m' + line + '\033[0m'
            return line

        lines = []
        diff = ndiff(self.old.split(), self.new.split())
        for line in diff:
            line = line.rstrip()
            if line[0] == '?':
                line = f' {line[1:]}'
            if line[0] in '+-':
                lines.append(line)
            else:
                lines[-1] += f'\n{line}'
        return '\n'.join((
            color_line(L) for L in lines
        ))

def validate_seasonal(profile: Profile):
    def print_entries(entry_type, entries):
        if not len(entries):
            return

        print(f'{entry_type}:')
        for entry in entries:
            if entry_type == 'changes':
                change = Change(*entry.values())
                print(f'  {change.description}')
                print(change.diff())
            else:
                print(f'  {entry}')
        print()

    success = True

    print(f'\n\033[94m{profile}\033[0m')
    with open(profile) as handle:
        lines = handle.read()
        data = f'{{"text": "{lines.encode("unicode_escape").decode("utf-8")}"}}'.encode('utf-8')
        request = Request('https://www.raidbots.com/api/simc/input/normalize',
                          data=data,
                          headers={'Content-Type': 'application/json',
                                   'User-Agent': 'simc-profile'},
                          method='POST')

        with urlopen(request) as response:
            body = response.read()
            encoding = response.info().get_content_charset('utf-8')
            parsed_json = loads(body.decode(encoding))

            fields = ('warnings', 'ignoredOptions', 'invalidCommands', 'changes')
            [print_entries(entry, parsed_json.get(entry)) for entry in fields]

            if len(parsed_json.get('changes', [])):
                print('Suggested Profile:')
                modified = parsed_json.get('input').split('\n')
                for line in modified:
                    if not line.startswith('# normalized by Raidbots'):
                        print(line)

            if any((len(parsed_json.get(entry, [])) for entry in fields)):
                success = False
            else:
                print(f'Ok! Raidbots Seasonal Configuration provided no suggestions.')

    return success

parser = ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filenames', nargs='*', type=Profile)
parser.add_argument('--validate', action='store_true', default=False, help='validate profiles')
parser.add_argument('--validate-seasonal', action='store_true', default=False)

args = parser.parse_args()

if not len(args.filenames):
    exit(0)

success = True

for profile in args.filenames:
    if args.validate:
        success &= validate(profile)

    if args.validate_seasonal:
        success &= validate_seasonal(profile)

if success:
    exit(0)
else:
    exit(1)
