from typing import List, Dict
import polars as pl

import math

def euclidean_distance(p1: Dict, p2: Dict) -> float:
    """Calculates the Euclidean distance between two points in 3D space."""
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2 + (p1['z'] - p2['z'])**2)



def calculate_ttfk(events: List[Dict]) -> float:
    """Calculates the Time to First Kill (TTFK) for a round."""
    for event in events:
        if event.get("event_name") == "player_death":
            return event.get("timestamp", 0.0)
    return 0.0

def calculate_time_to_bomb_plant(events: List[Dict]) -> float:
    """Calculates the time to bomb plant for a round."""
    for event in events:
        if event.get("event_name") == "bomb_planted":
            return event.get("timestamp", 0.0)
    return 0.0

def calculate_average_death_timestamp(events: List[Dict]) -> float:
    """Calculates the average death timestamp for a round."""
    death_timestamps = [event.get("timestamp", 0.0) for event in events if event.get("event_name") == "player_death"]
    if not death_timestamps:
        return 0.0
    return sum(death_timestamps) / len(death_timestamps)

def calculate_t_side_avg_dist_to_bombsite(demo) -> float:
    """Calculates the T-side average distance to bombsite for a round."""
    if demo is None:
        return 0.0

    bomb_planted_events = demo.events['bomb_planted']
    bombsite_locations = {}
    if not bomb_planted_events.is_empty():
        bombsite_mapping = {
            394: "A",
            486: "B"
        }
        bombsites = bomb_planted_events.group_by("site").agg(
            [
                pl.mean("user_X").alias("x"),
                pl.mean("user_Y").alias("y"),
                pl.mean("user_Z").alias("z"),
            ]
        )
        for site in bombsites.iter_rows(named=True):
            site_name = bombsite_mapping.get(site["site"])
            if site_name:
                bombsite_locations[site_name] = site

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate

    all_min_distances = []
    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]
        end_tick = freeze_end + (30 * tickrate)

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) & 
            (pl.col("tick") >= freeze_end) & 
            (pl.col("tick") <= end_tick) & 
            (pl.col("side") == "t")
        )

        if not round_ticks.is_empty():
            min_distances = []
            for tick in round_ticks.iter_rows(named=True):
                player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
                distances = [euclidean_distance(player_pos, loc) for loc in bombsite_locations.values()]
                if distances:
                    min_distances.append(min(distances))
            
            if min_distances:
                all_min_distances.extend(min_distances)

    if not all_min_distances:
        return 0.0

    return sum(all_min_distances) / len(all_min_distances)
