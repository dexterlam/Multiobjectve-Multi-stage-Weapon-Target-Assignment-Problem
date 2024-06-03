# Simulate threat data

## How to

Create simulated threats by running `create-threat-data.py`. The script outputs the simulated scenario in a .csv format.

## Parameters
`create-threat-data.py` uses `entities.json` and `threat-types.json` for the entity and threat configurations, respectively.
Additionally, the following paramters are intialized in `create-threat-data.py`:

- `NR_CRUISE_MISSILES`, `NR_DRONES`, `NR_HELICOPTERS`, `NR_FIXED_WING_AIRCRAFTS` for the composition of threats
- `time_betwwen_threats_s` which is a random function specifying the time between the arrival of the threats. 
- `THREAT_TARGETS` is a list of entities from `entities.json` to use as the target of the threats
- `THREAT_STARTING_DISTANCE_M` the distance from the target at which each threat should be simulated. 

An update is receive each second for each threat. 