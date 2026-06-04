from argparse import ArgumentParser
from pathlib import Path
import sys
import subprocess
from shared import ParsedOption, Profile, HEADER_OPTIONS

def validate_header_option(line):
    return ParsedOption(line).validate(HEADER_OPTIONS)

def generate_simc_input(profiles: list[Profile]):
    for profile in profiles:
        profile.validate()

        profile.params = []
        with open(profile) as handle:
            header = True
            for line in handle.readlines():
                line = line.strip()
                if not len(line):
                    continue
                if line[0] == '#':
                    if header and validate_header_option(line[1:].strip()):
                        line = line[1:].strip()
                    else:
                        line = ''
                else:
                    header = False

                if line != '':
                    profile.params.append(line)

def run_sim(binary: Path, profiles: list[str], prefix: list[str], suffix: list[str] = []):
    with subprocess.Popen([binary] + prefix + profiles + suffix, stdout=sys.stdout, stderr=sys.stderr) as proc:
        return proc.returncode

def print_dps_data(filename: Path):
    with subprocess.Popen(['jq', '[.sim.players[] | {name: .name, dps: .collected_data.dps}]', filename]) as proc:
        return proc.returncode

def save_profiles(binary: Path, profiles: list[Profile], location: Path):
    params = []
    for profile in profiles:
        params += profile.params
        params += [f'save={location}/{profile.expected_name()}.simc']
    return run_sim(binary, params, ['output=/dev/null'])

def run_profiles(binary: Path, profiles: list[Profile]):
    prefix = [
        'output=/dev/null',
        'target_error=0.05',
        'json=/tmp/out.json'
    ]
    return run_sim(binary, [line for profile in profiles for line in profile.params], prefix)

parser = ArgumentParser(prog='SimulationCraft Profile Runner')
parser.add_argument('filenames', nargs='+', type=Profile)
parser.add_argument('-b', '--binary', type=Path, required=True, metavar='PATH')
parser.add_argument('--save', type=Path, default=False, metavar='PATH', help='root directory to save all profiles')
parser.add_argument('--execute', action='store_true', default=False, help='execute profiles')

args = parser.parse_args()

generate_simc_input(args.filenames)

rc = []
if args.save:
    rc.append(save_profiles(args.binary, args.filenames, args.save))

if args.execute:
    rc.append(run_profiles(args.binary, args.filenames))
    rc.append(print_dps_data('/tmp/out.json'))

exit(max(rc))
