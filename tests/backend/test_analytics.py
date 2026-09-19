import math


def test_volatility_calculation():
    changes = [15, -20, 35, 10, -5]
    mean = sum(changes) / len(changes)
    variance = sum((x - mean) ** 2 for x in changes) / (len(changes) - 1)
    volatility = round(math.sqrt(variance), 2)
    assert volatility > 0
    assert isinstance(volatility, float)


def test_skill_gap_classification():
    user_rating = 1500
    tag_effective = 1200
    gap_delta = user_rating - tag_effective
    assert gap_delta == 300
    classification = "WEAKNESS" if gap_delta > 200 else "BALANCED"
    assert classification == "WEAKNESS"
