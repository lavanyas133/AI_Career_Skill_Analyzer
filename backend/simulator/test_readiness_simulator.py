
from backend.simulator.readiness_simulator import (
    simulate_learning_skill,
)


required = ["Python", "SQL", "Statistics"]
known = ["Python", "SQL"]


def test_already_known_skill():
    try:
        simulate_learning_skill(required, known, "Python")
    except ValueError as error:
        assert str(error) == "You already have this skill."
        print("PASS: Already-known skill is rejected.")
    else:
        raise AssertionError("Expected ValueError for an already-known skill.")


def test_invalid_skill():
    try:
        simulate_learning_skill(required, known, "Java")
    except ValueError as error:
        assert str(error) == (
            "This skill is not required for the selected role."
        )
        print("PASS: Invalid skill is rejected.")
    else:
        raise AssertionError("Expected ValueError for an invalid skill.")


if __name__ == "__main__":
    test_already_known_skill()
    test_invalid_skill()
    print("All validation tests passed!")
