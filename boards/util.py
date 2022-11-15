import logging
from typing import List, Optional, Tuple

from const.gameplay import Player
from errors.gameplay import BlockedPathingError, InvalidDropError, NoPathingFoundError, OutOfBoundError
from pieces.base import BasePiece, MovementBaseline
from pieces.king import KingPiece
from pieces.pawn import PawnPiece


class InvalidDroppingUtils:
    """
    Class for storing checks of invalid droppings
    """
    @classmethod
    def check_for_stuck_piece(cls,
                              piece: BasePiece,
                              board_black: Player,
                              board_dim: int,
                              position: Tuple[int, int]) -> bool:
        """
        Check if a piece is stuck (every available move is out of bound)
        This method is used to check for invalid drops

        Arguments:
        - piece (BasePiece):
            The piece being checked
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - position (Tuple[int, int]):
            The position of the piece

        Returns:
            bool: a value denoting if that piece is stuck (True) or not (False)
        """
        pov_coefficient = 1 if piece.player == board_black else -1
        for move_baseline in piece.moves_in_use:
            minimally_shifted_position = (
                position[0] + move_baseline.x_per_step * pov_coefficient,
                position[1] + move_baseline.y_per_step * pov_coefficient
            )
            if 0 <= minimally_shifted_position[0] < board_dim \
               or 0 <= minimally_shifted_position[1] < board_dim:
                return False  # not stuck. might be blocked, but that doesn't matter here

        return True

    # end check_for_stuck_piece()

    @classmethod
    def check_for_nifu(cls,
                       piece: PawnPiece,
                       board_dim: int,
                       board_matrix: List[List[BasePiece]],
                       position: Tuple[int, int]) -> bool:
        """
        Check if a pawn drop causes a nifu (two pawns in the same column)

        Arguments:
        - piece (PawnPiece):
            The pawn being checked
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - position (Tuple[int, int]):
            The position of the pawn

        Returns:
            bool: a value denoting if that pawn drop causes a nifu (True) or not (False)
        """
        # simply check all positions in the corresponding column
        for x_coordinate in range(board_dim):
            if board_matrix[x_coordinate][position[1]] is not None \
               and isinstance(board_matrix[x_coordinate][position[1]], PawnPiece) \
               and not piece.is_promoted \
               and piece.player == board_matrix[x_coordinate][position[1]].player:
                return True  # a pawn of the same side found on that column, nifu

        return False  # if nothing found, then no nifu

    # end check_for_nifu()

    @classmethod
    def check_for_uchifuzume(cls,
                             piece: PawnPiece,
                             board_matrix: List[List[BasePiece]],
                             position: Tuple[int, int]) -> bool:
        """
        Check if a pawn drop causes an uchifuzume (checkmate formed by dropping that pawn)

        Arguments:
        - piece (PawnPiece):
            The pawn being checked
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - position (Tuple[int, int]):
            The position of the pawn

        Returns:
            bool: a value denoting if that pawn drop causes an uchifuzume (True) or not (False)
        """
        # place the piece in, and scan for checkmate
        old_piece = board_matrix[position[0]][position[1]]  # storing for temporal replacement
        board_matrix[position[0]][position[1]] = piece  # add the new piece on

        is_checkmate = CheckmateUtils.is_checkmate(
            board_matrix=board_matrix, checking_player=piece.player
        )

        board_matrix[position[0]][position[1]] = old_piece  # return the old piece when done checking
        return is_checkmate

    # end check_for_uchifuzume()

# end InvalidDroppingUtils


class MovementUtils:
    """
    Class for movement utilities
    """
    @classmethod
    def is_valid_pathing(cls,
                         piece: BasePiece,
                         board_black: Player,
                         initial_position: Tuple[int, int],
                         final_position: Tuple[int, int]) -> Optional[Tuple[MovementBaseline, int]]:
        """
        Check if a pathing using a piece is valid.

        Arguments:
        - piece (BasePiece):
            The piece being checked
        - board_black (Player):
            The black player of the board
        - initial_position (Tuple[int, int]):
            Coordinate of the initial position of a pathing
        - final_position (Optional[Tuple[int, int]]):
            Coordinate of the final position of a pathing

        Returns:
            Optional[Tuple[MovementBaseline, int]]: A tuple describing the valid pathing to reach the
        final position in the form of (direction, step):
                - direction: MovementBaseLine
                - step: int
            If no valid pathing is available, this method returned None
        """
        pov_coefficient = 1 if piece.player == board_black else -1
        for baseline in piece.moves_in_use:
            # check invalid standing: if x_per_step/y_per_step is 0,
            # then position change for that axis should also be 0
            if final_position[0] - initial_position[0] != 0 and baseline.x_per_step == 0:
                continue
            if final_position[1] - initial_position[1] != 0 and baseline.y_per_step == 0:
                continue
            # count the number of steps; if standing, notate by None
            steps_required = (
                (final_position[0] - initial_position[0]) / (baseline.x_per_step * pov_coefficient)
                if baseline.x_per_step != 0 else None,
                (final_position[1] - initial_position[1]) / (baseline.y_per_step * pov_coefficient)
                if baseline.y_per_step != 0 else None,
            )
            # mismatched step counts means invalid move
            if steps_required[0] is not None and steps_required[1] is not None \
               and steps_required[0] != steps_required[1]:
                continue

            steps_required_flattened = steps_required[0] or steps_required[1]
            if steps_required_flattened is None:  # this is kind of a critical error
                logging.warning("Double None found in steps_required - is there a baseline"
                                "of direction (0, 0) defined for this piece?")
                continue
            if steps_required_flattened < 0:  # for consistency, step count should be positive
                continue
            if steps_required_flattened > 1 and baseline.step_limit:  # when limited, step must be 1
                continue

            # if passed all those failchecks, then there exists a valid baseline
            # thus the move will also be valid
            return (baseline, steps_required_flattened)

        # if no baseline works, then the move will be valid
        return None

    # end is_valid_pathing()

    @classmethod
    def is_blocked(cls,
                   piece: BasePiece,
                   position: Tuple[int, int],
                   board_black: Player,
                   board_dim: int,
                   board_matrix: List[List[BasePiece]],
                   baseline: MovementBaseline,
                   step: int) -> bool:
        """
        Check if a pathing of a piece is not blocked by any other pieces

        Arguments:
        - piece (BasePiece):
            The piece being checked
        - position (Tuple[int, int]):
            The initial position of the piece
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - baseline (MovementBaseline):
            Moving direction for the piece to be checked
        - step (int):
            Number of steps for the piece to be moved in the direction specified by baseline

        Returns:
            bool: a value denoting if the pathing is blocked (True) or not (False)
        """
        pov_coefficient = 1 if piece.player == board_black else -1
        final_position = (
            position[0] + baseline.x_per_step * step * pov_coefficient,
            position[1] + baseline.y_per_step * step * pov_coefficient
        )
        if final_position[0] < 0 or final_position[0] >= board_dim \
           or final_position[1] < 0 or final_position[1] >= board_dim:
            raise OutOfBoundError(final_position)

        if cls.is_valid_pathing(
            piece=piece,
            initial_position=position,
            final_position=final_position
        ) != (baseline, step):
            raise NoPathingFoundError(
                piece_type=type(piece),
                initial_position=position,
                final_position=final_position
            )

        for sub_step in range(1, step):
            new_position = (
                position[0] + baseline.x_per_step * sub_step * pov_coefficient,
                position[1] + baseline.y_per_step * sub_step * pov_coefficient
            )
            if board_matrix[new_position[0]][new_position[1]] is not None:
                return True  # a piece found blocking the path

        # final check: final position shouldn't be occupied by an allied piece
        if board_matrix[final_position[0]][final_position[1]] is not None \
           and board_matrix[final_position[0]][final_position[1]].player == piece.player:
            return True  # blocked at endpoint by an ally

        return False  # otherwise no blockade found, not a blocked path

    # end is_blocked()

    @classmethod
    def is_valid_move(cls,
                      piece: BasePiece,
                      board_black: Player,
                      board_dim: int,
                      board_matrix: List[List[BasePiece]],
                      initial_position: Tuple[int, int],
                      final_position: Tuple[int, int]) -> bool:
        """
        Check if a move using a piece is valid.

        Arguments:
        - piece (BasePiece):
            The piece being checked
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - initial_position (Tuple[int, int]):
            Coordinate of the initial position of a move
        - final_position (Optional[Tuple[int, int]]):
            Coordinate of the final position of a move

        Returns:
            bool: a value denoting if such move is valid (True) or not (False)
        """
        # check for pathing
        available_pathing = cls.is_valid_pathing(
            piece=piece,
            board_black=board_black,
            initial_position=initial_position,
            final_position=final_position
        )
        if not available_pathing:
            raise NoPathingFoundError(
                piece_type=type(piece),
                initial_position=initial_position,
                final_position=final_position
            )

        # final check: pathing not blocked = valid move
        if cls.is_blocked(
            piece=piece,
            position=initial_position,
            board_black=board_black,
            board_dim=board_dim,
            board_matrix=board_matrix,
            baseline=available_pathing[0],
            step=available_pathing[1]
        ):
            raise BlockedPathingError(
                piece_type=type(piece),
                initial_position=initial_position,
                final_position=final_position
            )

        return True

    # end is_valid_move()

    @classmethod
    def is_valid_drop(cls,
                      piece: BasePiece,
                      board_black: Player,
                      board_dim: int,
                      board_matrix: List[List[BasePiece]],
                      drop_position: Tuple[int, int]) -> bool:
        """
        Check if dropping a piece at a certain position is valid.
        This method assumes that the position is valid for the board, and it is
        an occupied position.

        Arguments:
        - piece (BasePiece):
            The piece being dropped
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - drop_position (Tuple[int, int]):
            Coordinate of the dropping position of that piece

        Returns:
            bool: a value denoting if that drop is valid (True) or not (False)
        """
        # stuck check
        if InvalidDroppingUtils.check_for_stuck_piece(
            piece=piece,
            board_black=board_black,
            board_dim=board_dim,
            board_matrix=board_matrix,
            drop_position=drop_position
        ):
            raise InvalidDropError(
                piece_type=type(piece),
                coordinate=drop_position,
                violated_rule="piece not being stuck after drop"
            )

        # nifu check (must be pawn)
        if InvalidDroppingUtils.check_for_nifu(
            piece=piece,
            board_dim=board_dim,
            board_matrix=board_matrix,
            drop_position=drop_position
        ) and isinstance(piece, PawnPiece):
            raise InvalidDropError(
                piece_type=type(piece),
                coordinate=drop_position,
                violated_rule="nifu"
            )

        # uchifuzume check (must be pawn)
        if InvalidDroppingUtils.check_for_uchifuzume(
            piece=piece,
            board_matrix=board_matrix,
            drop_position=drop_position
        ) and isinstance(piece, PawnPiece):
            raise InvalidDropError(
                piece_type=type(piece),
                coordinate=drop_position,
                violated_rule="post-pawn-drop checkmate"
            )

        # a drop must not violate ANY invalid dropping pattern to be considered valid
        return True

    # end is_valid_drop()

    @classmethod
    def get_threatening_list(
        cls,
        board_black: Player,
        board_dim: int,
        board_matrix: List[List[BasePiece]],
        position: Tuple[int, int],
        threatening_player: Player
    ) -> List[Tuple[BasePiece, Tuple[int, int], MovementBaseline, int]]:
        """
        Get the list of pieces of a side threatening a position on the board

        Arguments:
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - position (Tuple[int, int]):
            The position to check for threats
        - threatening_player (Player):
            The player being supposed to be threatening the position

        Returns:
            List[Tuple[BasePiece, Tuple[int, int], MovementBaseline, int]]: a list of tuples
            denoting the threats towards the given position, containing those attributes:
                - BasePiece: the piece threatening
                - Tuple[int, int]: the position of that piece
                - MovementBaseline: the direction to threaten the initial position
                - int: number of steps in that direction to reach the initial position
        """
        threat_list = []

        for x_coor in range(board_dim):
            for y_coor in range(board_dim):
                if board_matrix[x_coor][y_coor] is None:  # empty cell, ignore
                    continue
                if board_matrix[x_coor][y_coor].player != threatening_player:  # not threat side
                    continue
                pathing = cls.is_valid_pathing(
                    piece=board_matrix[x_coor][y_coor],
                    initial_position=(x_coor, y_coor),
                    final_position=position
                )
                if pathing is None:  # no pathing found, no threat
                    continue
                if cls.is_blocked(
                    piece=board_matrix[x_coor][y_coor],
                    position=(x_coor, y_coor),
                    board_black=board_black,
                    board_dim=board_dim,
                    board_matrix=board_matrix,
                    baseline=pathing[0],
                    step=pathing[1]
                ):  # the path is blocked, thus no threat
                    continue

                # everything checks out, a threat is detected
                threat_list.append(
                    (board_matrix[x_coor][y_coor], (x_coor, y_coor), pathing[0], pathing[1])
                )

        return threat_list

    # end get_threatening_list()

# end MovementUtils


class CheckmateUtils:
    """
    Class for checkmate utilities
    """
    @classmethod
    def get_checking_list(
        cls,
        board_black: Player,
        board_dim: int,
        board_matrix: List[List[BasePiece]],
        checking_player: Player
    ) -> Tuple[
        Tuple[int, int],
        List[Tuple[BasePiece, Tuple[int, int], MovementBaseline, int]]
    ]:
        """
        Get the list of pieces of a side checking their opponent

        Arguments:
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - checking_player (Player):
            The player being supposed to be performing a check

        Returns: a tuple of two components:
            Tuple[int, int]: position of the checked king
            List[Tuple[BasePiece, Tuple[int, int], MovementBaseline, int]]: a list of tuples
            denoting the checking pieces, containing those attributes:
                - BasePiece: the piece checking
                - Tuple[int, int]: the position of that piece
                - MovementBaseline: the direction to check the opponent
                - int: number of steps in that direction to reach the opponent's king
        """
        king_position = None
        for x_coor in range(board_dim):
            for y_coor in range(board_dim):
                if isinstance(board_matrix[x_coor][y_coor], KingPiece) \
                   and board_matrix[x_coor][y_coor].player != checking_player:
                    king_position = (x_coor, y_coor)

        return MovementUtils.get_threatening_list(
            board_black=board_black,
            board_dim=board_dim,
            board_matrix=board_matrix,
            position=king_position,
            threatening_player=checking_player
        )

    # end get_checking_list()

    @classmethod
    def is_checkmate(cls,
                     board_black: Player,
                     board_dim: int,
                     board_matrix: List[List[BasePiece]],
                     checked_side_captured_pieces: List[BasePiece],
                     checking_player: Player) -> bool:
        """
        Check if a checkmate is made on the board

        Arguments:
        - board_black (Player):
            The black player of the board
        - board_dim (int):
            The dimension of the board
        - board_matrix (List[List[BasePiece]]):
            The matrix (list of list) denoting the pieces currently standing on the current board
        - checked_side_captured_pieces (List[BasePiece]):
            List of pieces captured by a side supposed to be checkmated.
        - checking_player (Player):
            The player being supposed to be performing a checkmate

        Returns:
            bool: a value denoting if the given side performs a checkmate (True) or not (False)
        """
        king_position, checking_threats = cls.get_checking_list(
            board_black=board_black,
            board_dim=board_dim,
            board_matrix=board_matrix,
            checking_player=checking_player
        )
        assert isinstance(board_matrix[king_position[0]][king_position[1]], KingPiece)
        king_piece = board_matrix[king_position[0]][king_position[1]]

        # case 0: no threat
        if len(checking_threats) == 0:
            return False

        # try to run the king
        for baseline in board_matrix[king_position[0]][king_position[1]].moves_in_use:
            if not MovementUtils.is_blocked(piece=king_piece,
                                            position=king_position,
                                            board_black=board_black,
                                            board_dim=board_dim,
                                            board_matrix=board_matrix,
                                            baseline=baseline,
                                            step=1):
                return False  # a way to flee exists, thus not a checkmate

        # if not fleeable, try to block
        # if there are two or more threats, a block is futile
        if len(checking_threats) >= 2:
            return True  # checkmate
        # otherwise, try blocking the threat by either moving an allied piece to intercept
        _, threat_position, threat_baseline, threat_step = checking_threats[0]
        for sub_step in range(1, threat_step):
            blockable_position = (
                threat_position[0] + threat_baseline * sub_step,
                threat_position[1] + threat_baseline * sub_step
            )

            if len(
                MovementUtils.get_threatening_list(
                    board_black=board_black,
                    board_dim=board_dim,
                    board_matrix=board_matrix,
                    position=blockable_position,
                    threatening_player=not checking_player
                )
            ) > 0:
                return False  # a way to block exists, thus not a checkmate

            for captured_piece in checked_side_captured_pieces:
                if MovementUtils.is_valid_drop(
                    piece=captured_piece,
                    board_black=board_black,
                    board_dim=board_dim,
                    board_matrix=board_matrix,
                    drop_position=blockable_position
                ):
                    return False  # a way to block exists, thus not a checkmate

        # if no blocking option is possible, then it's a checkmate
        return True

    # end is_checkmate()

# end CheckmateUtils
