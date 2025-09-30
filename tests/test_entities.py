from src.cs2_analyzer.domain.entities import Player, Team, Round, Game

def test_player():
    player = Player(steam_id=123, name="Test Player", team="Terrorist")
    assert player.steam_id == 123
    assert player.name == "Test Player"
    assert player.team == "Terrorist"
