import pytest

from dungeondice.lib import dice


@pytest.mark.parametrize("rollstring,expected", [
    # Should pass
    ('1d20', [
        dice.Rollgroup.from_string('1d20'),
    ]),
    ('2x1d20', [
        dice.Rollgroup.from_string('1d20'),
        dice.Rollgroup.from_string('1d20'),
    ]),
    ('2xd20', [
        dice.Rollgroup.from_string('d20'),
        dice.Rollgroup.from_string('d20'),
    ]),
    ('2xd20(piercing)', [
        dice.Rollgroup.from_string('d20(piercing)'),
        dice.Rollgroup.from_string('d20(piercing)'),
    ]),
    ('2xd20,2d20', [
        dice.Rollgroup.from_string('d20'),
        dice.Rollgroup.from_string('d20'),
        dice.Rollgroup.from_string('2d20'),
    ]),
    ('2x2d20(poison)+d8(piercing)+d20', [
        dice.Rollgroup.from_string('2d20(poison)+d8(piercing)+d20'),
        dice.Rollgroup.from_string('2d20(poison)+d8(piercing)+d20'),
    ]),
    # Should fail
    ('1d', False),
    ('100d', False),
    ('5d10l6', False),
    ('d8(piercing))', False),
    ('d8(())piercing))', False),
    ('2xd20xd20', False),
    ('2xd202xd20', False),
])
def test_parser(rollstring, expected):
    """Test our rolling 'templating'.

    These tests onlt concern themselves with 'does this rollstring parse'.
    Rolling logic is tested in more specific tests.
    """
    parser = dice.Parser()

    if expected:
        assert parser.parse(rollstring) == expected
    else:
        with pytest.raises(ValueError):
            parser.parse(rollstring)


@pytest.mark.parametrize("rollstring,expected_result", [
    ('d20+5+d10', 9),
    ('d20-1+d10', 3),
    ('d20-1+2d10', 5),
    ('d20-1(piercing)+2d10(poison)', 5),
    ('d20-d10(poison)', 0),
])
def test_rollgroups(rollstring, expected_result):
    """Test creating and rolling rollgroups.

    We fumble rolls with a 2 to check totals.
    """
    rollgroup = dice.Rollgroup.from_string(rollstring)
    rollgroup.roll(fumble=2)
    assert rollgroup.total == expected_result


@pytest.mark.parametrize("rollstring,expected_rollset,expected_result", [
    ('d20', dice.Rollset('d20', 1, 20, 1, False, False), 2),
    ('2d20', dice.Rollset('2d20', 2, 20, 2, False, False), 4),
    ('2d20k1', dice.Rollset('2d20k1', 2, 20, 1, True, False), 2),
    ('2d20kl1', dice.Rollset('2d20kl1', 2, 20, 1, False, False), 2),
    ('2', dice.Rollset('2', 0, 0, 0, False, False), 2),
    ('2d20k1(poison)', dice.Rollset('2d20k1', 2, 20, 1, True, False), 2),
])
def test_rollsets(rollstring, expected_rollset, expected_result):
    """Test creating and rolling rollsets.

    We fumble rolls with a 2 to check totals.
    """
    rollset = dice.Rollset.from_string(rollstring, False)
    assert rollset == expected_rollset

    rollset.roll(fumble=2)
    assert rollset.total == expected_result


@pytest.mark.parametrize("rollstring,expected", [
    ('2d20k1(poison)', 'poison'),
])
def test_comments(rollstring, expected):
    """Test adding comments to a rollset."""
    rollset = dice.Rollset.from_string(rollstring, False)
    assert rollset.comment == expected
