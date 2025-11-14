from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Player:
    steam_id: int
    name: str
    team: str
    position: Dict[str, float] = None

@dataclass
class Team:
    name: str
    players: List[Player]

@dataclass
class Round:
    round_number: int
    winner: str
    events: List[Dict]
    positions: List[Dict] = None

@dataclass
class Game:
    map_name: str
    teams: List[Team]
    rounds: List[Round]
