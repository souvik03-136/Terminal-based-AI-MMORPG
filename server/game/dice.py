import random
from typing import Tuple

class Dice:
    """D&D-style dice roller."""

    @staticmethod
    def roll(sides: int, count: int = 1) -> Tuple[int, list]:
        rolls = [random.randint(1, sides) for _ in range(count)]
        return sum(rolls), rolls

    @staticmethod
    def roll_d20() -> int:
        return random.randint(1, 20)

    @staticmethod
    def roll_d6() -> int:
        return random.randint(1, 6)

    @staticmethod
    def advantage_roll() -> int:
        """Roll d20 twice, take higher (advantage mechanic)."""
        return max(random.randint(1, 20), random.randint(1, 20))

    @staticmethod
    def disadvantage_roll() -> int:
        """Roll d20 twice, take lower (disadvantage mechanic)."""
        return min(random.randint(1, 20), random.randint(1, 20))