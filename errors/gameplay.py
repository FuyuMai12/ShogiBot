from typing import Literal, Tuple, Type

from const.gameplay import player_string_mappings, Player
from util.kif import format_coordinates


class GameplayException(Exception):
    """
    An error occured due to breaking gameplay
    """
    pass


class GameNotInitiatedError(GameplayException):
    """
    Exception raised when an action is made before the first player is decided
    """
    pass

# end GameNotInitiatedError


class GameEndedError(GameplayException):
    """
    Exception raised when an action is made after the game ended
    """
    pass

# end GameEndedError


class IncorrectPlayerError(GameplayException):
    """
    Exception raised when an action is made by an incorrect player
    """
    def __init__(self,
                 attempted_player: Player,
                 actual_player: Player):
        error_message = f"Expected an action from {player_string_mappings[actual_player]}, " \
                        f"got {player_string_mappings[attempted_player]} instead."
        super().__init__(error_message)

    # end __init__()

# end IncorrectPlayerError


class OutOfBoundError(GameplayException):
    """
    Exception raised when an input coordinate is out of bound
    """
    def __init__(self, coordinate: Tuple[int, int]):
        error_message = f"Coordinate {format_coordinates(coordinate)} out of bound."
        super().__init__(error_message)

    # end __init__()

# end OutOfBoundError


class EmptyCellError(GameplayException):
    """
    Exception raised when an initial cell for a piece move is empty
    """
    def __init__(self, coordinate: Tuple[int, int]):
        error_message = f"Coordinate {format_coordinates(coordinate)} has no piece."
        super().__init__(error_message)

    # end __init__()

# end EmptyCellError


class PieceNotOwnedError(GameplayException):
    """
    Exception raised when a cell commanded to be moved is not
    of the current player's control
    """
    def __init__(self, coordinate: Tuple[int, int],
                 attempted_player: Literal['junior', 'senior'],
                 actual_owner: Literal['junior', 'senior']):
        error_message = f"Coordinate {format_coordinates(coordinate)} has a piece " \
                        f"being commanded by {attempted_player}, " \
                        f"yet it's actually owned by {actual_owner}."
        super().__init__(error_message)

    # end __init__()

# end PieceNotOwnedError


class NotPromotableError(GameplayException):
    """
    Exception raised when a piece is ordered to promote while
    its type cannot do so
    """
    def __init__(self, piece_type: Type,
                 coordinate: Tuple[int, int]):
        error_message = f"Impossible to promote the {piece_type} " \
                        f"at coordinate {format_coordinates(coordinate)}."
        super().__init__(error_message)

    # end __init__()

# end NotPromotableError


class NotInPromotionZoneError(GameplayException):
    """
    Exception raised when a piece is ordered to promote while
    its initial and final position are both outside of the promotion zone
    """
    def __init__(self,
                 initial_position: Tuple[int, int],
                 final_position: Tuple[int, int],):
        error_message = f"Piece moving from {format_coordinates(initial_position)} to " \
                        f"{format_coordinates(final_position)} cannot be promoted " \
                        "due to not being in promotion zone."
        super().__init__(error_message)

    # end __init__()

# end NotPromotableError


class NoPathingFoundError(GameplayException):
    """
    Exception raised when a movement of a piece from a position to another
    is not possible due to no valid pathing is found
    """
    def __init__(self, piece_type: Type,
                 initial_position: Tuple[int, int],
                 final_position: Tuple[int, int]):
        error_message = f"Impossible to move a {piece_type} " \
                        f"from coordinate {format_coordinates(initial_position)} " \
                        f"to coordinate {format_coordinates(final_position)}."
        super().__init__(error_message)

    # end __init__()

# end NoPathingFoundError


class BlockedPathingError(GameplayException):
    """
    Exception raised when a movement of a piece from a position to another
    is not possible due to no valid pathing is found
    """
    def __init__(self, piece_type: Type,
                 initial_position: Tuple[int, int],
                 final_position: Tuple[int, int]):
        error_message = f"The path to move a {piece_type} " \
                        f"from coordinate {format_coordinates(initial_position)} " \
                        f"to coordinate {format_coordinates(final_position)} is blocked."
        super().__init__(error_message)

    # end __init__()

# end BlockedPathingError


class OccupiedCellError(GameplayException):
    """
    Exception raised when an initial cell for a drop is occupied
    """
    def __init__(self, coordinate: Tuple[int, int]):
        error_message = f"A piece is already at coordinate {format_coordinates(coordinate)}."
        super().__init__(error_message)

    # end __init__()

# end OccupiedCellError


class DroppingPieceNotExistedError(GameplayException):
    """
    Exception raised when the piece ordered to be drop doesn't exist
    """
    def __init__(self, piece_type: type, piece_id: int):
        error_message = f"A {piece_type} with id #{piece_id} " \
                         "doesn't exist in the current player's capture pool."
        super().__init__(error_message)

    # end __init__()

# end DroppingPieceNotExistedError


class InvalidDropError(GameplayException):
    """
    Exception raised when the drop violates some of the rules
    """
    def __init__(self, piece_type: type, coordinate: Tuple[int, int], violated_rule: str):
        error_message = f"A {piece_type} drop at coordinate {format_coordinates(coordinate)} " \
                        f"is invalid for violating the rule of {violated_rule}."
        super().__init__(error_message)

    # end __init__()

# end DroppingPieceNotExistedError


class SelfExposureMoveError(GameplayException):
    """
    Exception raised when a move causes that player to be checked
    """
    def __init__(self, piece_type: Type,
                 initial_position: Tuple[int, int],
                 final_position: Tuple[int, int]):
        error_message = f"A move of {piece_type} " \
                        f"from coordinate {format_coordinates(initial_position)} to coordinate " \
                        f"{format_coordinates(final_position)} exposes the player to a check."
        super().__init__(error_message)

    # end __init__()

# end SelfExposureMoveError


class SelfExposureDropError(GameplayException):
    """
    Exception raised when a drop causes that player to be checked
    """
    def __init__(self, piece_type: Type,
                 coordinate: Tuple[int, int]):
        error_message = f"A drop of {piece_type} " \
                        f"to coordinate {format_coordinates(coordinate)} exposes the player to a check."
        super().__init__(error_message)

    # end __init__()

# end SelfExposureDropError
