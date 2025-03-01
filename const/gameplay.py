from enum import Flag


class Player(Flag):
    """
    Standard enum to denote and wrap players.
    Junior is True, Senior is False.
    """
    Senior = False
    Junior = True


player_string_mappings = {
    Player.Senior: 'senior',
    Player.Junior: 'junior',
}
