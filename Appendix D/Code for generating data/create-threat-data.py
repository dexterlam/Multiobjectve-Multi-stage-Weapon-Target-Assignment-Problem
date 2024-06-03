#%%
import json
from typing import List, Tuple, Dict
import random
import pandas as pd
from geopy.distance import geodesic
from geopy.point import Point
import math
from tqdm import tqdm
import datetime

#%%

#number of each threat in the entire scenario
NR_CRUISE_MISSILES = 20
NR_DRONES = 0
NR_HELICOPTERS = 10
NR_FIXED_WING_AIRCRAFTS = 7

time_betwwen_threats_s =  lambda: random.randint(0,10)  # approximate time between eta of the threats. the threats are arriving in a random order

with open("entities.json") as f:
    entities = json.load(f)

THREAT_TARGETS = [entities["weapon_system_A"]]  # end destination of the threats. each threat is assigned an entity from THREAT_TARGETS at random
THREAT_STARTING_DISTANCE_M = 40000  # the distance from the threat target at which the threats will start

with open("threat-types.json") as f:
    threat_types = json.load(f)


SECONDS_BETWEEN_UPDATES = 5


#%%

def move_towards_target(threat: dict, seconds_between_updates: int) -> pd.DataFrame:
    """
    Simulate movement towards a target location and write updates to a pandas dataframe.
    """
    current_position = Point(threat["start_location"][0], threat["start_location"][1])
    target_position = Point(threat["target"][0], threat["target"][1])
    distance_to_target = geodesic(current_position, target_position).meters
    bearing_to_target = bearing(current_position, target_position)
    time = 0  # Initialize time

    updates: List[Dict[str,int | float]] = []
    meters_to_move = seconds_between_updates*threat_types[threat["type"]]["speed_ms"]

    while distance_to_target >= meters_to_move:
        new_position = geodesic(meters=meters_to_move).destination(current_position, bearing_to_target)
        current_position = new_position
        distance_to_target = geodesic(current_position, target_position).meters

        updates.append({'time': time, 'uid': threat["uid"], "type": threat["type"], 'latitude': new_position.latitude, 'longitude': new_position.longitude})
        time += seconds_between_updates

    return pd.DataFrame(updates)  


def create_threat_queue(cruise_missiles: int, drones: int, helicopters: int, fixed_wing_aircrafts: int, threat_targets: List[dict], starting_dist_m: int) -> List[dict]:
    threats = []
    uid = 0
    for _ in range(cruise_missiles):
        target = random.choice(threat_targets)
        threat = {"uid": uid, "type": "cruise_missile", "start_location": generate_coordinate(s=(target["location_lat"], target["location_lon"]), m=starting_dist_m), "target": (target["location_lat"], target["location_lon"])}
        threats.append(threat)
        uid+=1
    for _ in range(drones):
        target = random.choice(threat_targets)
        threat = {"uid": uid, "type": "drone", "start_location": generate_coordinate(s=(target["location_lat"], target["location_lon"]), m=starting_dist_m),  "target": (target["location_lat"], target["location_lon"])}
        threats.append(threat)
        uid+=1
    for _ in range(helicopters):
        target = random.choice(threat_targets)
        threat = {"uid": uid, "type": "helicopter", "start_location": generate_coordinate(s=(target["location_lat"], target["location_lon"]), m=starting_dist_m),  "target": (target["location_lat"], target["location_lon"])}
        threats.append(threat)
        uid+=1
    for _ in range(fixed_wing_aircrafts):
        target = random.choice(threat_targets)
        threat = {"uid": uid, "type": "fixed_wing_aircraft", "start_location": generate_coordinate(s=(target["location_lat"], target["location_lon"]), m=starting_dist_m), "target": (target["location_lat"], target["location_lon"])}
        threats.append(threat)
        uid+=1
    random.shuffle(threats)
    return threats


def bearing(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> int:
    """
    Calculate the bearing between two points.

    Params
    point_a: Tuple of (latitude, longitude) for the first point
    point_b: Tuple of (latitude, longitude) for the second point
    
    return: bearing in degrees
    """
    lat1, lon1 = math.radians(point_a[0]), math.radians(point_a[1])
    lat2, lon2 = math.radians(point_b[0]), math.radians(point_b[1])

    dlon = lon2 - lon1
    x = math.cos(lat2) * math.sin(dlon)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360

    return bearing


def generate_coordinate(s: Tuple[float, float], m: int) -> Tuple[float, float]:
    """
    Find point m meters from starting point

    Params
    s: Tuple of (latitude, longitude) for the starting point
    m: desired distance in meters
    
    return: Tuple of (latitude, longitude) a point m meters from s
    """
    lat, lon = s
    angle = random.randint(0, 360) 
    origin = Point(lat, lon)
    destination = geodesic(meters=m).destination(origin, angle)
    return (destination.latitude, destination.longitude)

#%%
if __name__ == "__main__":
    simulated_scenario = pd.DataFrame()
    threats = create_threat_queue(cruise_missiles=NR_CRUISE_MISSILES, drones=NR_DRONES, helicopters=NR_HELICOPTERS, fixed_wing_aircrafts=NR_FIXED_WING_AIRCRAFTS, threat_targets=THREAT_TARGETS, starting_dist_m=THREAT_STARTING_DISTANCE_M)
    max_time = 0

    for t in tqdm(threats):
        t["times_series"] = move_towards_target(t,SECONDS_BETWEEN_UPDATES)
        if max_time < max(t["times_series"]["time"]):
            max_time = max(t["times_series"]["time"])
    for t in threats:
        time_diff = max_time - max(t["times_series"]["time"]) + time_betwwen_threats_s()
        t["times_series"]["time"] = t["times_series"]["time"] + time_diff
        max_time = max(t["times_series"]["time"])
        simulated_scenario = pd.concat([simulated_scenario, t["times_series"]], ignore_index=True)
    simulated_scenario=simulated_scenario.sort_values("time")
    t = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%d%H%M")
    simulated_scenario.to_csv(f"scenario-{t}.csv", index=False)
# %%
