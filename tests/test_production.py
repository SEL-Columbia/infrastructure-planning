from infrastructure_planning.production import adjust_for_losses


def test_adjust_for_losses():
    x = 100
    assert adjust_for_losses(x, 25) * (1 - 0.25) == x
    assert adjust_for_losses(x, 25, 10) * (1 - 0.10) * (1 - 0.25) == x
    assert adjust_for_losses(x, 25, 10) * (1 - 0.25) * (1 - 0.10) == x
    assert adjust_for_losses(x, 100) == 0
