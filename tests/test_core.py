from orbit_core import plan_goal, risk_for


def test_plan_has_five_steps():
    p = plan_goal("Build a small website")
    assert len(p.steps) == 5
    assert p.goal == "Build a small website"


def test_high_risk_actions_flagged():
    assert risk_for("delete old files") == "HIGH"
    assert risk_for("make a payment") == "HIGH"


def test_general_research_is_low_risk():
    assert risk_for("research open-source web frameworks") == "LOW"
