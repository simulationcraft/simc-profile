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

class ParsedOption:
    pass

class Option:
    key: str
    ignore_value: bool
    values: list[str]
    case_sensitive: bool

    def __init__(self, key, values=[], ignore_value=False, case_sensitive=True):
        self.key = key
        self.values = values
        self.ignore_value = ignore_value
        self.case_sensitive = case_sensitive

    def __eq__(self, other: ParsedOption):
        if self.key != other.key:
            return False
        if self.ignore_value:
            return True
        if self.case_sensitive:
            return other.value in self.values
        else:
            return other.value.lower() in self.values

class Options:
    options: list[Option]
    keys: set()

    def __init__(self, *options):
        self.options = options
        self.keys = set((o.key for o in options))

    def __contains__(self, other):
        return other in self.options

# class (handled separately as value depends on filename)
SIMC_OPTIONS = Options(
    Option('level', ['90']),
    Option('spec', [spec for specs in SPEC_NAMES.values() for spec in specs]),
    # copied from util::race_type_string and util::parse_race_type
    Option('race',
           ['blood_elf', 'dark_iron_dwarf', 'dracthyr_alliance', 'dracthyr_horde', 'draenei', 'dwarf', 'gnome', 'goblin', 'haranir_alliance', 'haranir_horde', 'highmountain_tauren', 'human', 'kul_tiran', 'lightforged_draenei', 'maghar_orc', 'mechagnome', 'night_elf', 'nightborne', 'orc', 'pandaren', 'pandaren_alliance', 'pandaren_horde', 'tauren', 'troll', 'undead', 'void_elf', 'vulpera', 'worgen', 'zandalari_troll', 'forsaken', 'dracthyr', 'earthen', 'earthen_dwarf', 'haranir', 'harronir', 'harronir_horde', 'harronir_alliance'],
           case_sensitive=False),
    Option('timeofday', ['day', 'daytime', 'night', 'nighttime']),
    # copied from util::role_type_string
    Option('role', ['attack', 'spell', 'hybrid', 'dps', 'tank', 'heal', 'auto']),
    # copied from util::position_type_string
    Option('position', ['none', 'back', 'front', 'ranged_back', 'ranged_front']),
    # talents
    Option('talents', ignore_value=True),
    # gear
    Option('head', ignore_value=True),
    Option('neck', ignore_value=True),
    Option('shoulders', ignore_value=True),
    Option('shoulder', ignore_value=True),
    Option('chest', ignore_value=True),
    Option('waist', ignore_value=True),
    Option('legs', ignore_value=True),
    Option('leg', ignore_value=True),
    Option('feet', ignore_value=True),
    Option('foot', ignore_value=True),
    Option('wrists', ignore_value=True),
    Option('wrist', ignore_value=True),
    Option('hands', ignore_value=True),
    Option('hand', ignore_value=True),
    Option('finger1', ignore_value=True),
    Option('finger2', ignore_value=True),
    Option('ring1', ignore_value=True),
    Option('ring2', ignore_value=True),
    Option('trinket1', ignore_value=True),
    Option('trinket2', ignore_value=True),
    Option('back', ignore_value=True),
    Option('main_hand', ignore_value=True),
    Option('off_hand', ignore_value=True),
    # class options
    # copied from warlock_t::create_action_warlock
    Option('warlock.default_pet', ['sayaad', 'succubus', 'incubus', 'felguard']),
)
HEADER_OPTIONS = Options(
    Option('desired_targets', ignore_value=True),
    Option('fight_style', ['patchwerk', 'castingpatchwerk', 'dungeonslice']),
    Option('source', ['default']),
    Option('potion', ignore_value=True),
    Option('flask', ignore_value=True),
    Option('food', ignore_value=True),
    Option('augmentation', ignore_value=True),
    Option('temporary_enchant', ignore_value=True),
)

class Profile:
    path: Path
    params: list[str]

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
            return False

        class_name, trailing_fragment, spec_name = self.path_parts()
        if not class_name and not trailing_fragment and not spec_name:
            return False

        if class_name not in SPEC_NAMES.keys():
            print(f'Profile {self} is not in a `profiles/<class>/` directory.')
            return False

        if spec_name not in SPEC_NAMES[class_name]:
            print(f'Profile {self} does not contain a valid specialization name. It should include one of {", ".join(SPEC_NAMES[class_name])}.')
            return False

        # python has no way to nicely test if a string contains only printable ascii characters :)
        if not all((c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in trailing_fragment[len(spec_name):])):
            print(f'Profile {self} trailing fragment {trailing_fragment[len(spec_name):]} is not alphanumeric.')
            return False

    def expected_name(self):
        class_name, trailing_fragment, _ = self.path_parts()
        return f'{class_name}_{trailing_fragment}'

    def path_parts(self):
        path_parts = PurePath.relative_to(self.path.resolve(), Path(__file__).resolve(), walk_up=True).parts[2:]
        if path_parts[0] != 'profiles':
            print(f'Profile {self} is not in the `profiles/` directory.')
            return False, False, False

        trailing_fragment = path_parts[2].split('.')[:-1][0]
        return path_parts[1], trailing_fragment, trailing_fragment.split('_')[0]

class ParsedOption:
    key: str
    operator: str
    value: str

    parsed: bool

    def __init__(self, line):
        self.parsed = True
        try:
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
        except IndexError:
            self.key = line
            self.parsed = False

    def __str__(self):
        if not self.parsed:
            return f'Invalid Option {self.key}'
        return f'{self.key}{self.operator}{self.value}'

    def validate_class(self, profile: Profile):
        class_name, _, _ = profile.path_parts()
        return self.parsed and self.key == class_name

    def validate_class_value(self, profile: Profile):
        return self.parsed and self.validate_class(profile) and self.value == profile.expected_name()

    def validate(self, options: Options):
        return self.parsed and self.validate_key(options) and self.validate_value(options)

    def validate_key(self, options: Options):
        return self.parsed and self.key in options.keys

    def validate_value(self, options: Options):
        return self.parsed and self in options
