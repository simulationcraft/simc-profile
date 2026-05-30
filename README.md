# [SimulationCraft](https://www.simulationcraft.org/) Profiles [![CI](https://github.com/simulationcraft/simc-profile/workflows/CI/badge.svg)](https://github.com/simulationcraft/simc-profile/actions?query=workflow%3ACI)

## What are Profiles?
SimulationCraft profiles contained within this repository are sample gear and talent configurations for the current tier. These profiles are somewhat arbitrary, and no expectation that profiles are optimal should exist.

There are some basic rules that all profiles must follow:
* Files match the pattern `<class>/<spec>[a-zA-Z0-9_]*.simc`.
* Character name must match file path.
* All gear must be obtainable in game.
* Talent strings must be valid. Due to implementation details of the talent system, they may require frequent updates.
* May only override defaults for consumables.
* May include context-relevant options such as `fight_style`, and `desired_targets`.

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
