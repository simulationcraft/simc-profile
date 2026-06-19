from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys

from shared import ParsedOption, Profile, Options, HEADER_OPTIONS, SIMC_OPTIONS, SPEC_NAMES

def handle_header_line(line: str, deferral_list: Options, profile: Profile):
    option = ParsedOption(line, profile)
    if option.validate(HEADER_OPTIONS):
        option_definition = option.option(HEADER_OPTIONS)
        if option_definition.scope == 'player' and option_definition.simc_option:
            deferral_list.append(line)
            return ''
        else:
            return line
    return ''

def generate_simc_input(profiles: list[Profile]):
    for profile in profiles:
        profile.validate()

        profile.params = []
        deferred_options = []
        push_deferred_options = False
        with open(profile) as handle:
            header = True
            for line in handle.readlines():
                line = line.strip()
                if not len(line):
                    continue
                if line[0] == '#' and header:
                    line = handle_header_line(line[1:].strip(), deferred_options, profile)
                elif line[0] == '#' and not header:
                    line = ''
                else:
                    option = ParsedOption(line, profile)
                    if option.key in SPEC_NAMES.keys() and option.validate(SIMC_OPTIONS):
                        push_deferred_options = True
                    header = False

                if line != '':
                    profile.params.append(line)
                if push_deferred_options:
                    profile.params += deferred_options
                    deferred_options = []

def run_sim(binary: Path, profiles: list[str], prefix: list[str], suffix: list[str] = []):
    proc = subprocess.Popen([binary] + prefix + profiles + suffix, stdout=sys.stdout, stderr=sys.stderr)
    proc.wait()
    return proc.returncode

def print_dps_data(filename: Path):
    proc = subprocess.Popen(['jq', '[.sim.players[] | {name: .name, dps: .collected_data.dps}]', filename])
    proc.wait()
    return proc.returncode

def save_profiles(binary: Path, profiles: list[Profile], location: Path):
    params = [
        'single_actor_batch=1',
    ]
    for profile in profiles:
        params += profile.params
        params += [f'save={location}/{profile.expected_name()}.simc']
    return run_sim(binary, params, ['output=/dev/null'])

def run_profiles(binary: Path, profiles: list[Profile], location: Path):
    prefix = [
        'single_actor_batch=1',
        'output=/dev/null',
        'target_error=0.05',
        f'json={location}/output.json',
        f'html={location}/output.html'
    ]
    return run_sim(binary, [line for profile in profiles for line in profile.params], prefix)

parser = ArgumentParser(prog='SimulationCraft Profile Runner')
parser.add_argument('filenames', nargs='*', type=Profile)
parser.add_argument('-b', '--binary', type=Path, required=True, metavar='PATH')
parser.add_argument('--save', type=Path, default=False, metavar='PATH', help='root directory to save all profiles')
parser.add_argument('--execute', type=Path, default=False, metavar='PATH', help='root directory to save profile output')

args = parser.parse_args()

generate_simc_input(args.filenames)

if not len(args.filenames):
    exit(0)

rc = []
if args.save:
    rc.append(save_profiles(args.binary, args.filenames, args.save))

if args.execute:
    rc.append(run_profiles(args.binary, args.filenames, args.execute))
    rc.append(print_dps_data(f'{args.execute}/output.json'))

print(rc)
exit(max(rc))
