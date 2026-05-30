import argparse
from pathlib import Path, PurePath

SPEC_NAMES = {
    'deathknight': ['blood', 'frost', 'unholy'],
    'demonhunter': ['devourer', 'havoc', 'vengeance'],
    'druid': ['balance', 'feral', 'guardian'],
    'evoker': ['devastation', 'augmentation'],
    'hunter': ['beast_mastery', 'marksmanship', 'survival'],
    'mage': ['arcane', 'fire', 'frost'],
    'monk': ['brewmaster', 'windwalker'],
    'paladin': ['protection', 'retribution'],
    'priest': ['shadow'],
    'rogue': ['assassination', 'outlaw', 'subtlety'],
    'shaman': ['elemental', 'enhancement'],
    'warlock': ['affliction', 'demonology', 'destruction'],
    'warrior': ['arms', 'fury', 'protection']
}

# if true, option is valid regardless of right hand side
# if list, option is valid if list contains right hand side
VALID_SIMC_OPTIONS = {
    'level': ['90'],
    # class (handled separately as value depends on filename)
    'spec': [spec for specs in SPEC_NAMES.values() for spec in specs],
    # race, copied from util::race_type_string and util::parse_race_type
    'race': ['blood_elf', 'dark_iron_dwarf', 'dracthyr_alliance', 'dracthyr_horde', 'draenei', 'dwarf', 'gnome', 'goblin', 'haranir_alliance', 'haranir_horde', 'highmountain_tauren', 'human', 'kul_tiran', 'lightforged_draenei', 'maghar_orc', 'mechagnome', 'night_elf', 'nightborne', 'orc', 'pandaren', 'pandaren_alliance', 'pandaren_horde', 'tauren', 'troll', 'undead', 'void_elf', 'vulpera', 'worgen', 'zandalari_troll',
             'forsaken', 'dracthyr', 'earthen', 'earthen_dwarf', 'haranir', 'harronir', 'harronir_horde', 'harronir_alliance'],
    'timeofday': ['day', 'night'],
    # talents
    'talents': True,
    # gear
    'head': True,
    'neck': True,
    'shoulders': True,
    'shoulder': True,
    'chest': True,
    'waist': True,
    'legs': True,
    'leg': True,
    'feet': True,
    'foot': True,
    'wrists': True,
    'wrist': True,
    'hands': True,
    'hand': True,
    'finger1': True,
    'finger2': True,
    'ring1': True,
    'ring2': True,
    'trinket1': True,
    'trinket2': True,
    'back': True,
    'main_hand': True,
    'off_hand': True,
    # class options
    'warlock.default_pet': ['sayaad', 'succubus', 'incubus', 'felguard']
}

VALID_PROFILE_OPTIONS = {
    'source': ['default'],
    'role': ['attack', 'spell', 'hybrid', 'dps', 'tank', 'heal', 'auto'],
    'position': ['none', 'back', 'front', 'ranged_back', 'ranged_front'],
    # consumables
    'potion': True,
    'flask': True,
    'food': True,
    'augmentation': True,
    'temporary_enchant': True,
}

class Option:
    key: str
    operator: str
    value: str

    valid_options_source: dict

    def __init__(self, line, valid_options):
        if len(line) == 0:
            return

        self.valid_options = valid_options

        collect_key = ""
        escaped = False
        quoted = False
        for c in line:
            if escaped:
                escaped = False
            if c == '\\':
                escaped = True
            if c == '"' and not quoted:
                quoted = True
            if c == '"' and quoted:
                quoted = False
            if not escaped and not quoted and c in '+=':
                self.key = collect_key
                break
            else:
                collect_key += c
        self.operator = ''
        for c in line[len(collect_key)]:
            if c in '+=/':
                self.operator += c
            else:
                break
        self.value = line[len(collect_key) + len(self.operator):]

    def __str__(self):
        return f'{self.key}{self.operator}{self.value}'

    def expected_name(self, class_name, trailing_fragment):
        return f'{class_name}_{trailing_fragment}'

    def is_class(self, class_name, trailing_fragment):
        return self.value == self.expected_name(class_name, trailing_fragment)

    def is_valid_key(self):
        return self.key in self.valid_options.keys()

    def is_valid(self):
        if not self.is_valid_key():
            return False
        values = self.valid_options[self.key]
        if isinstance(values, bool):
            return True
        else:
            return self.value.lower() in values

def parse_profile_option(line):
    option = Option(line, VALID_PROFILE_OPTIONS)
    if not option.is_valid_key():
        print(f'Profile {path} has invalid Profile option {option.key}.')
    elif not option.is_valid():
        print(f'Profile {path} has invalid Profile option {option}.')

def parse_simc_option(line):
    option = Option(line, VALID_SIMC_OPTIONS)
    if option.key == class_name:
        if not option.is_class(class_name, trailing_fragment):
            print(f'Profile {path} has invalid name {option}. Expected {option.expected_name(class_name, trailing_fragment)}.')
        return
    if not option.is_valid_key():
        print(f'Profile {path} has invalid SimulationCraft option {option.key}.')
    elif not option.is_valid():
        print(f'Profile {path} has invalid SimulationCraft option {option}.')

parser = argparse.ArgumentParser(prog='SimulationCraft Profile Validator')
parser.add_argument('filename', nargs='+', type=Path)

args = parser.parse_args()

for path in args.filename:
    if path.parts[-1].split('.')[1] != 'simc':
        print(f'Skipping path {path}.')
        continue

    if not path.exists():
        print(f'Path {path} does not exist.')

    if len(path.parts) != 3:
        print(f'Path {path} is not a relative path of the expected length.')

    path_parts = PurePath.relative_to(path.resolve(), Path(__file__).resolve(), walk_up=True).parts[2:]
    if len(path_parts) != 3:
        print(f'File {path} is not in the correct location.')

    if path_parts[0] != 'profiles':
        print(f'Profile {path} is not in the `profiles/` folder.')

    if path_parts[1] not in SPEC_NAMES.keys():
        print(f'Profile {path} is not in a `profiles/<class>/` folder.')

    # profiles/<class_name>/<trailing_fragment>.simc
    # profiles/<class_name>/<spec_name><unnamed>.simc
    # <class_name>=<class_name>_<spec_name><unnamed>
    class_name = path_parts[1]
    trailing_fragment = path_parts[2].split('.')[:-1][0]
    spec_name = trailing_fragment.split('_')[0]

    if spec_name not in SPEC_NAMES[class_name]:
        print(f'Profile {path} does not contain a valid specialization name. Try one of {", ".join(SPEC_NAMES[class_name])}.')

    # python has no way to nicely test if a string contains only printable ascii characters :)
    if not all((c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in trailing_fragment[len(spec_name):])):
        print(f'Profile {path} trailing fragment {trailing_fragment[len(spec_name):]} is not alphanumeric.')

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
                parse_simc_option(line)
