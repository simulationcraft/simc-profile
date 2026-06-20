from pathlib import Path, PurePath
from collections.abc import Callable, Iterable

def flatten(collection: Iterable):
    for element in collection:
        if isinstance(element, Iterable) and not isinstance(element, str):
            for subelement in flatten(element):
                yield subelement
        else:
            yield element

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
    key: str | list[str]
    alias: str
    ignore_value: bool
    values: list[str]
    case_sensitive: bool
    scope: str
    simc_option: bool
    validate_fn: Callable[[ParsedOption], bool] | None
    required: bool
    unique_value: bool

    def __init__(self, key, values=None,
                 case_sensitive=True, scope=None, simc_option=True,
                 validate_fn=None, required=False, unique_value=False,
                 alias=None):
        if scope is None:
            print(key, values)
            assert scope is not None
        self.key = key
        self.alias = alias
        self.values = values if values is not None else []
        self.ignore_value = True if values is None else False
        self.case_sensitive = case_sensitive
        self.scope = scope
        self.simc_option = simc_option
        self.validate_fn = validate_fn
        self.required = required
        self.unique_value = unique_value

    def __str__(self):
        return f"{self.scope} option " \
            f"'{self.key if self.alias is None else self.alias}'" \
            f"{'' if self.ignore_value else f' (possible value{'s' if len(self.values) > 1 else ''}: {', '.join(self.values)})'}"

    def __eq__(self, other: ParsedOption):
        if isinstance(other, ParsedOption):
            if isinstance(self.key, str):
                if self.key != other.key:
                    return False
            if isinstance(self.key, list):
                if other.key not in self.key:
                    return False
            if self.validate_fn is not None:
                return self.validate_fn(other)
            if self.ignore_value:
                return True
            if self.case_sensitive:
                return other.value in self.values
            else:
                return other.value.lower() in self.values
        assert False
        return False

    def __hash__(self):
        return hash((repr(self.key), self.ignore_value, repr(self.values),
                     self.case_sensitive, self.scope, self.simc_option,
                     self.validate_fn, self.required, self.unique_value))

class Options:
    options: list[Option]
    keys: set()
    required: set()

    def __init__(self, *options):
        self.options = options
        self.keys = set(flatten((option.key for option in options)))
        self.required = set(option for option in options if option.required)

    def __contains__(self, other):
        return other in self.options

    def __iter__(self):
        for option in self.options:
            yield option

def validate_class_option(option: ParsedOption):
    success = option.value == option.profile.expected_name()
    if not success:
        print(f'Profile {option.profile} has invalid name {option}. Expected {option.profile.expected_name()}.')
    return success

SIMC_OPTIONS = Options(
    Option(list(SPEC_NAMES.keys()), alias='<class name>', validate_fn=validate_class_option, scope='sim', required=True),
    Option('level', ['90'], scope='player', required=True),
    Option('spec', [spec for specs in SPEC_NAMES.values() for spec in specs], scope='player', required=True),
    # copied from util::race_type_string and util::parse_race_type
    Option('race',
           ['blood_elf', 'dark_iron_dwarf', 'dracthyr_alliance', 'dracthyr_horde', 'draenei', 'dwarf', 'gnome', 'goblin', 'haranir_alliance', 'haranir_horde', 'highmountain_tauren', 'human', 'kul_tiran', 'lightforged_draenei', 'maghar_orc', 'mechagnome', 'night_elf', 'nightborne', 'orc', 'pandaren', 'pandaren_alliance', 'pandaren_horde', 'tauren', 'troll', 'undead', 'void_elf', 'vulpera', 'worgen', 'zandalari_troll', 'forsaken', 'dracthyr', 'earthen', 'earthen_dwarf', 'haranir', 'harronir', 'harronir_horde', 'harronir_alliance'],
           case_sensitive=False, scope='player', required=True),
    Option('timeofday', ['day', 'daytime', 'night', 'nighttime'], scope='player'),
    # copied from util::role_type_string
    Option('role', ['attack', 'spell', 'hybrid', 'dps', 'tank', 'heal', 'auto'], scope='player'),
    # copied from util::position_type_string
    Option('position', ['none', 'back', 'front', 'ranged_back', 'ranged_front'], scope='player'),
    # talents
    Option('talents', scope='player', required=True),
    # gear
    Option('head', scope='player', required=True),
    Option('neck', scope='player', required=True),
    Option(['shoulder', 'shoulders'], alias='shoulder', scope='player', required=True),
    Option('chest', scope='player', required=True),
    Option('waist', scope='player', required=True),
    Option(['leg', 'legs'], alias='leg', scope='player', required=True),
    Option(['foot', 'feet'], alias='foot', scope='player', required=True),
    Option(['wrist', 'wrists'], alias='wrist', scope='player', required=True),
    Option(['hand', 'hands'], alias='hand', scope='player', required=True),
    Option(['finger1', 'ring1'], alias='finger1', scope='player', required=True),
    Option(['finger2', 'ring2'], alias='finger2', scope='player', required=True),
    Option('trinket1', scope='player', required=True),
    Option('trinket2', scope='player', required=True),
    Option('back', scope='player', required=True),
    Option('main_hand', scope='player', required=True),
    Option('off_hand', scope='player'),
    # consumables
    Option('potion', scope='player'),
    Option('flask', scope='player'),
    Option('food', scope='player'),
    Option('augmentation', scope='player'),
    Option('temporary_enchant', scope='player'),
    # class options
    # copied from warlock_t::create_action_warlock
    Option('warlock.default_pet', ['sayaad', 'succubus', 'incubus', 'felguard'], scope='player'),
)

HEADER_OPTIONS = Options(
    Option('ptr', ['0', '1'], scope='sim'),
    Option('desired_targets', scope='sim'),
    Option('fight_style', ['patchwerk', 'castingpatchwerk', 'dungeonslice'], scope='sim'),
    Option('profile_type', simc_option=False, scope='header')
)

class Profile:
    path: Path
    params: list[str]
    observed_options: set[Option]

    def __init__(self, path):
        self.path = Path(path)
        self.observed_options = set()

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

        class_name, spec_name, suffix = self.path_parts()
        if not class_name or not spec_name:
            return False

        if class_name not in SPEC_NAMES.keys():
            print(f'Profile {self} is not in a `profiles/<class>/` directory.')
            return False

        if spec_name not in SPEC_NAMES[class_name]:
            print(f'Profile {self} does not contain a valid specialization name. It should include one of {", ".join(SPEC_NAMES[class_name])}.')
            return False

        # python has no way to nicely test if a string contains only printable ascii characters :)
        if not all((c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in suffix)):
            print(f'Profile {self} suffix {suffix} is not alphanumeric.')
            return False

        return True

    def expected_name(self):
        class_name, spec_name, suffix = self.path_parts()
        return f'{class_name}_{spec_name}{"" if suffix == "" else "_"}{suffix}'

    def path_parts(self):
        path_parts = PurePath.relative_to(self.path.resolve(), Path(__file__).resolve(), walk_up=True).parts[2:]
        if path_parts[0] != 'profiles':
            print(f'Profile {self} is not in the `profiles/` directory.')
            return False, False, False

        trailing_fragment = path_parts[2].split('.')[:-1][0]
        spec_name = trailing_fragment.split('_')[0]
        suffix = '_'.join(trailing_fragment.split('_')[1:])
        return path_parts[1], spec_name, suffix

    def related_profiles(self):
        return self.path.parent.glob(f'{self.path_parts()[1]}*.simc')

class ParsedOption:
    profile: Profile

    key: str
    operator: str
    value: str

    parsed: bool

    def __init__(self, line: str, profile: Profile):
        self.profile = profile

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

    def option(self, options: Options):
        return self in options and next((o for o in options if o == self)) or None

    def validate(self, options: Options):
        return self.parsed and self.validate_key(options) and self.validate_value(options)

    def validate_key(self, options: Options):
        return self.parsed and self.key in options.keys

    def validate_value(self, options: Options):
        return self.parsed and self in options
