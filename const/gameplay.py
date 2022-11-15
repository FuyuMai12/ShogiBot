from enum import Enum


class Player(Enum):
    """
    Standard enum to denote and wrap players.
    Junior is True, Senior is False.
    """
    Senior = False
    Junior = True


player_string_mappings = {
    Player.Senior: 'senior',
    Player.Junior: 'junior'
}
