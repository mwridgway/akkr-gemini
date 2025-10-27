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


def calculate_ct_side_forward_presence_count(demo) -> float:
    """Calculates the CT-side forward presence count for a round."""
    if demo is None:
        return 0.0

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate
    t_spawn = demo.t_spawn
    ct_spawn = demo.ct_spawn

    forward_counts = []
    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]
        end_tick = freeze_end + (30 * tickrate)

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end) &
            (pl.col("tick") <= end_tick) &
            (pl.col("side") == "ct")
        )

        if not round_ticks.is_empty():
            forward_players = 0
            for tick in round_ticks.iter_rows(named=True):
                player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
                dist_to_ct_spawn = euclidean_distance(player_pos, ct_spawn)
                dist_to_t_spawn = euclidean_distance(player_pos, t_spawn)

                if dist_to_t_spawn < dist_to_ct_spawn:
                    forward_players += 1
            
            # Get the number of unique ticks to average the forward_players
            num_ticks = round_ticks.select(pl.col("tick").n_unique()).item()
            if num_ticks > 0:
                forward_counts.append(forward_players / num_ticks)

    if not forward_counts:
        return 0.0

    return sum(forward_counts) / len(forward_counts)


def calculate_player_spacing(demo, side: str) -> float:
    """Calculates the average player spacing for a given side."""
    if demo is None:
        return 0.0

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate

    avg_spacings = []
    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]
        end_tick = freeze_end + (30 * tickrate)

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end) &
            (pl.col("tick") <= end_tick) &
            (pl.col("side") == side)
        )

        if not round_ticks.is_empty():
            for tick_num in round_ticks.select("tick").unique().to_series():
                tick_players = round_ticks.filter(pl.col("tick") == tick_num)
                if len(tick_players) > 1:
                    distances = []
                    player_pos = tick_players.select(["X", "Y", "Z"]).to_dicts()
                    for i in range(len(player_pos)):
                        for j in range(i + 1, len(player_pos)):
                            p1 = {'x': player_pos[i]['X'], 'y': player_pos[i]['Y'], 'z': player_pos[i]['Z']}
                            p2 = {'x': player_pos[j]['X'], 'y': player_pos[j]['Y'], 'z': player_pos[j]['Z']}
                            distances.append(euclidean_distance(p1, p2))
                    
                    if distances:
                        avg_spacings.append(sum(distances) / len(distances))

    if not avg_spacings:
        return 0.0

    return sum(avg_spacings) / len(avg_spacings)


def calculate_rotation_timing(demo) -> float:
    """Calculates the average rotation timing for a round."""
    if demo is None:
        return 0.0

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate
    bombsite_locations = demo.bombsite_locations

    rotation_times = []

    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end)
        )

        if round_ticks.is_empty():
            continue

        for player_id in round_ticks.select("player_steamid").unique().to_series():
            player_ticks = round_ticks.filter(pl.col("player_steamid") == player_id).sort("tick")
            
            last_site = None
            exit_tick = None

            for tick in player_ticks.iter_rows(named=True):
                player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
                current_site = None

                for site_name, site_loc in bombsite_locations.items():
                    if euclidean_distance(player_pos, site_loc) <= site_loc["radius"]:
                        current_site = site_name
                        break
                
                if last_site and not current_site:
                    exit_tick = tick["tick"]

                if not last_site and current_site and exit_tick:
                    rotation_time = (tick["tick"] - exit_tick) / tickrate
                    rotation_times.append(rotation_time)
                    exit_tick = None

                last_site = current_site

    if not rotation_times:
        return 0.0

    return sum(rotation_times) / len(rotation_times)


def calculate_rotation_success_rate(demo, survival_time: int = 30) -> float:
    """Calculates the average rotation success rate for a round."""
    if demo is None:
        return 0.0

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate
    bombsite_locations = demo.bombsite_locations
    player_death_events = demo.events.get("player_death", pl.DataFrame())

    total_rotations = 0
    successful_rotations = 0

    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end)
        )

        if round_ticks.is_empty():
            continue

        for player_id in round_ticks.select("player_steamid").unique().to_series():
            player_ticks = round_ticks.filter(pl.col("player_steamid") == player_id).sort("tick")
            
            last_site = None
            exit_tick = None

            for tick in player_ticks.iter_rows(named=True):
                player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
                current_site = None

                for site_name, site_loc in bombsite_locations.items():
                    if euclidean_distance(player_pos, site_loc) <= site_loc["radius"]:
                        current_site = site_name
                        break
                
                if last_site and not current_site:
                    exit_tick = tick["tick"]

                if not last_site and current_site and exit_tick:
                    total_rotations += 1
                    rotation_end_tick = tick["tick"]
                    survival_deadline = rotation_end_tick + (survival_time * tickrate)

                    player_death = player_death_events.filter(
                        (pl.col("user_steamid") == player_id) &
                        (pl.col("tick") > rotation_end_tick) &
                        (pl.col("tick") <= survival_deadline)
                    )

                    if player_death.is_empty():
                        successful_rotations += 1
                    
                    exit_tick = None

                last_site = current_site

    if total_rotations == 0:
        return 0.0

    return successful_rotations / total_rotations


def calculate_engagement_success_on_rotation(demo) -> float:
    """Calculates the engagement success on rotation."""
    if demo is None:
        return 0.0

    ticks = demo.ticks
    rounds = demo.rounds
    tickrate = demo.tickrate
    bombsite_locations = demo.bombsite_locations
    player_death_events = demo.events.get("player_death", pl.DataFrame())

    total_engagements = 0
    successful_engagements = 0

    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]

        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end)
        )

        if round_ticks.is_empty():
            continue

        for player_id in round_ticks.select("player_steamid").unique().to_series():
            player_ticks = round_ticks.filter(pl.col("player_steamid") == player_id).sort("tick")
            
            last_site = None
            exit_tick = None

            for tick in player_ticks.iter_rows(named=True):
                player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
                current_site = None

                for site_name, site_loc in bombsite_locations.items():
                    if euclidean_distance(player_pos, site_loc) <= site_loc["radius"]:
                        current_site = site_name
                        break
                
                if last_site and not current_site:
                    exit_tick = tick["tick"]

                if not last_site and current_site and exit_tick:
                    rotation_start_tick = exit_tick
                    rotation_end_tick = tick["tick"]

                    # Check for engagements during rotation
                    rotation_engagements = player_death_events.filter(
                        (pl.col("tick") > rotation_start_tick) &
                        (pl.col("tick") <= rotation_end_tick)
                    )

                    if not rotation_engagements.is_empty():
                        for engagement in rotation_engagements.iter_rows(named=True):
                            total_engagements += 1
                            attacker = engagement.get("attacker_steamid")
                            victim = engagement.get("user_steamid")

                            if attacker == player_id and victim != player_id:
                                # Check if the rotating player survived the engagement
                                player_died_in_engagement = player_death_events.filter(
                                    (pl.col("tick") > rotation_start_tick) &
                                    (pl.col("tick") <= rotation_end_tick) &
                                    (pl.col("user_steamid") == player_id)
                                ).is_empty()
                                if player_died_in_engagement:
                                    successful_engagements += 1

                    exit_tick = None

                last_site = current_site

    if total_engagements == 0:
        return 0.0

    return successful_engagements / total_engagements


def calculate_round_win_percentage(demo) -> float:
    """Calculates the T-side round win percentage for set executes."""
    if demo is None:
        return 0.0

    rounds = demo.rounds
    bomb_planted_events = demo.events.get("bomb_planted", pl.DataFrame())

    if bomb_planted_events.is_empty():
        return 0.0

    planted_rounds = bomb_planted_events.select("round_num").unique().to_series()
    
    total_planted_rounds = len(planted_rounds)
    if total_planted_rounds == 0:
        return 0.0

    won_planted_rounds = rounds.filter(
        (pl.col("round_num").is_in(planted_rounds)) &
        (pl.col("winner_side") == "t")
    ).height

    return won_planted_rounds / total_planted_rounds


def calculate_entry_success_rate(demo, entry_time_window: int = 15) -> float:
    """Calculates the T-side entry success rate for set executes."""
    if demo is None:
        return 0.0

    rounds = demo.rounds
    ticks = demo.ticks
    tickrate = demo.tickrate
    player_death_events = demo.events.get("player_death", pl.DataFrame())
    bombsite_locations = demo.bombsite_locations

    total_executes = 0
    successful_entries = 0

    for r in rounds.iter_rows(named=True):
        round_num = r["round_num"]
        freeze_end = r["freeze_end"]
        
        round_ticks = ticks.filter(
            (pl.col("round_num") == round_num) &
            (pl.col("tick") >= freeze_end) &
            (pl.col("side") == "t")
        )

        if round_ticks.is_empty():
            continue

        # Simplified: Assume an execute happens in any T-side round for now.
        # A more complex implementation would detect coordinated pushes.
        total_executes += 1
        
        entry_window_end = freeze_end + (entry_time_window * tickrate)

        entry_ticks = round_ticks.filter(
            (pl.col("tick") <= entry_window_end)
        )

        entry_success = False
        for tick in entry_ticks.iter_rows(named=True):
            player_pos = {'x': tick['X'], 'y': tick['Y'], 'z': tick['Z']}
            for site_loc in bombsite_locations.values():
                if euclidean_distance(player_pos, site_loc) <= site_loc.get("radius", 200): # Default radius
                    # Check if player survived the entry
                    player_id = tick["player_steamid"]
                    death_event = player_death_events.filter(
                        (pl.col("user_steamid") == player_id) &
                        (pl.col("tick") <= entry_window_end)
                    )
                    if death_event.is_empty():
                        entry_success = True
                        break
            if entry_success:
                break
        
        if entry_success:
            successful_entries += 1

    if total_executes == 0:
        return 0.0

    return successful_entries / total_executes


def calculate_trade_efficiency(demo, trade_time_window: int = 5) -> float:
    """Calculates the T-side trade efficiency for set executes."""
    if demo is None:
        return 0.0

    player_death_events = demo.events.get("player_death", pl.DataFrame())
    tickrate = demo.tickrate

    if player_death_events.is_empty():
        return 0.0

    t_deaths = 0
    traded_deaths = 0

    t_players = demo.t_players
    ct_players = demo.ct_players

    for death in player_death_events.iter_rows(named=True):
        if death.get("user_side") == "t":
            t_deaths += 1
            death_tick = death["tick"]
            trade_window_end = death_tick + (trade_time_window * tickrate)

            # Check for a CT death within the trade window
            trade_kill = player_death_events.filter(
                (pl.col("tick") > death_tick) &
                (pl.col("tick") <= trade_window_end) &
                (pl.col("user_side") == "ct") &
                (pl.col("attacker_side") == "t")
            )

            if not trade_kill.is_empty():
                traded_deaths += 1

    if t_deaths == 0:
        return 0.0

    return traded_deaths / t_deaths
