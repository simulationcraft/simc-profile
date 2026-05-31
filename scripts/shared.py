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
    # copied from util::race_type_string and util::parse_race_type
    'race': ['blood_elf', 'dark_iron_dwarf', 'dracthyr_alliance', 'dracthyr_horde', 'draenei', 'dwarf', 'gnome', 'goblin', 'haranir_alliance', 'haranir_horde', 'highmountain_tauren', 'human', 'kul_tiran', 'lightforged_draenei', 'maghar_orc', 'mechagnome', 'night_elf', 'nightborne', 'orc', 'pandaren', 'pandaren_alliance', 'pandaren_horde', 'tauren', 'troll', 'undead', 'void_elf', 'vulpera', 'worgen', 'zandalari_troll', 'forsaken', 'dracthyr', 'earthen', 'earthen_dwarf', 'haranir', 'harronir', 'harronir_horde', 'harronir_alliance'],
    'timeofday': ['day', 'daytime', 'night', 'nighttime'],
    # copied from util::role_type_string
    'role': ['attack', 'spell', 'hybrid', 'dps', 'tank', 'heal', 'auto'],
    # copied from util::position_type_string
    'position': ['none', 'back', 'front', 'ranged_back', 'ranged_front'],
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
    # copied from warlock_t::create_action_warlock
    'warlock.default_pet': ['sayaad', 'succubus', 'incubus', 'felguard']
}

VALID_PROFILE_OPTIONS = {
    'desired_targets': True,
    'fight_style': ['patchwerk', 'dungeonslice', 'castingpatchwerk'],
    'source': ['default'],
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
        quoted = False
        for c in line:
            if c == '"' and not quoted:
                quoted = True
            if c == '"' and quoted:
                quoted = False
            if not quoted and c in '+=':
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

class Profile:
    path: Path

    def __init__(self, path):
        self.path = Path(path)

    def __str__(self):
        return str(self.path)

    def __fspath__(self):
        return self.path.__fspath__()

    def validate(self):
        # profiles/<class_name>/<trailing_fragment>.simc
        # profiles/<class_name>/<spec_name><unnamed>.simc
        # <class_name>=<class_name>_<spec_name><unnamed>
        if not self.path.exists():
            print(f'Path {self} does not exist.')
            return

        class_name, trailing_fragment, spec_name = self.path_parts()
        if class_name not in SPEC_NAMES.keys():
            print(f'Profile {self} is not in a `profiles/<class>/` directory.')
            return

        if spec_name not in SPEC_NAMES[class_name]:
            print(f'Profile {self} does not contain a valid specialization name. Try one of {", ".join(SPEC_NAMES[class_name])}.')
            return

        # python has no way to nicely test if a string contains only printable ascii characters :)
        if not all((c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in trailing_fragment[len(spec_name):])):
            print(f'Profile {self} trailing fragment {trailing_fragment[len(spec_name):]} is not alphanumeric.')
            return

    def path_parts(self):
        path_parts = PurePath.relative_to(self.path.resolve(), Path(__file__).resolve(), walk_up=True).parts[2:]
        if path_parts[0] != 'profiles':
            print(f'Profile {self} is not in the `profiles/` directory.')
            return

        trailing_fragment = path_parts[2].split('.')[:-1][0]
        return path_parts[1], trailing_fragment, trailing_fragment.split('_')[0]
