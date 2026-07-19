# [SimulationCraft](https://www.simulationcraft.org/) Profiles [![ci](https://github.com/simulationcraft/simc-profile/actions/workflows/ci.yml/badge.svg)](https://github.com/simulationcraft/simc-profile/actions/workflows/ci.yml)

## What are Profiles?
SimulationCraft profiles contained within this repository are sample gear and talent configurations for the current tier. These profiles are somewhat arbitrary, and no expectation that profiles are optimal should exist.

## Why have Profiles moved?
Profiles historically were an important component used to test SimulationCraft prior to the implementation of several features that allow for testing to occur that is less vulnerable to talent and gear configuration rot.

Profiles also used to provide a more human-accessible version of default APLs in a plaintext form, but that has also been superceded by the `ActionPriorityLists/` directory in the `simulationcraft/simc` repository.

As a result, moving Profiles to a new home will allow for improvements in validation and make contributing a more streamlined experience without additional burden on the primary `simulationcraft/simc` repository.

## How can I get help?
If you have questions about a specific profile, reaching out to its current maintainer is oftentimes easiest in the respective Class Discord server.

If you have more specific SimC related questions, reaching out in the [SimCMinMax](https://discord.gg/tFR2uvK) (#simulationcraft) server is also an option.

## How can I contribute?
We always welcome Pull Requests for new or updated profiles for any specialization that is supported by SimulationCraft.

A tutorial on how to create a Pull Request is available [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

If you have further questions, feel free to contact us through the SimCMinMax Discord.

## What options are allowed in Profiles?
Profiles include a group of standard SimC options as well as an optional set of Header options.

Header options are commented out (the first non-whitespace character on the line is `#`) and come before all SimC options.
E.g.
```
# Header Options (this is a comment and not required)
# ptr=1
# fight_style=patchwerk

warrior=warrior_arms
# Header Options beyond this point are discarded
# ... rest of profile
```

Profiles may have the following set of Header options:
- `ptr` (`1` or `0`, configures CI to use `ptr` spell data, check against `mimiron` seasonal rules and suggestions, indicates profile is for future tier)
- `desired_targets`
- `fight_style` (`patchwerk`, `castingpatchwerk`, `dungeonslice`)
- `profile_type` (`default`, `m+`, `raid`, informs users what content the profile is intended for)

SimC options are all standard options permitted in the SimC textual configuration interface. Reference the [SimulationCraft Wiki](https://github.com/simulationcraft/simc/wiki) for examples and documentation.

Profiles must have the following set of SimC options:
- `level` (only current maximum level permitted)
- `spec` (must match filename)
- `race`
- `talents`
- `head`
- `neck`
- `shoulder` (or `shoulders`)
- `chest`
- `waist`
- `leg` (or `legs`)
- `foot` (or `feet`)
- `wrist` (or `wrists`)
- `hand` (or `hands`)
- `finger1` (or `ring1`)
- `finger2` (or `ring2`)
- `trinket1`
- `trinket2`
- `back`
- `main_hand`

Profiles may have the following set of SimC options:
- `timeofday` (includes `day` and `night`. night elf racial)
- `role`
- `position`
- `off_hand`
- `potion`
- `flask`
- `food`
- `augmentation`
- `temporary_enchant`
- `warlock.default_pet` (`sayaad`, `succubus`, `incubus`, `felguard`)

Profiles may have the following header options:

## What rules must Profiles follow?

Each profile for a class must be placed in the `profiles/<class>` directory.
Each profile filename must match the pattern `<spec>[_a-zA-Z0-9]*.simc`.
E.g.
```
profiles/warrior/arms.simc
profiles/mage/frost_spellslinger.simc
```

The class and specialization referenced in the profile must correspond with a maintained SimC class module. Alternate specialization names are not permitted.

The actor's name must match the full filename, replacing path separators with `_`.
E.g.
```
$ cat profiles/warrior/arms.simc
warrior=warrior_arms
```

Each profile must contain all required options as listed in the previous section.
