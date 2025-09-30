from src.cs2_analyzer.application.metrics import calculate_t_side_avg_dist_to_bombsite

def test_calculate_t_side_avg_dist_to_bombsite():
    assert calculate_t_side_avg_dist_to_bombsite(None) == 0.0
