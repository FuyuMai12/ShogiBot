import json
import logging
from pydoc import locate
from typing import Dict, List, Optional, Tuple

from const.gameplay import Player
from errors.gameplay import (
    DroppingPieceNotExistedError, EmptyCellError, GameEndedError, GameNotInitiatedError,
    GameplayException, IncorrectPlayerError, NotInPromotionZoneError, NotPromotableError,
    OccupiedCellError, OutOfBoundError, PieceNotOwnedError
)
from pieces.base import BasePiece
from util.board import InvalidDroppingUtils, MovementUtils
from util.kif import (
    Kif, drop_indicator, full_arabic_nums, full_kanji_nums,
    promote_indicator, side_symbols
)

default_profile_path = "profiles/boards/standard.json"


class ShogiBoard():
    """
    Class for a Shogi board.
    """
    def __init__(self, first_move: Player):
        file = open(default_profile_path, 'r', encoding='utf-8')
        imported_dict = json.load(file)

        self.dim: int = imported_dict['dimension']

        self.black: Player = first_move
        self.white: Player = ~self.black

        self.next_action: Player = self.black

        self.winner: Player = None

        self.board: List[List[BasePiece]] = [
            [
                None for _ in range(self.dim)
            ]
            for _ in range(self.dim)
        ]

        self.captured_pieces: Dict[Player, List[BasePiece]] = {
            self.black: [],
            self.white: []
        }

        incremental_id = 0

        for unit_dict in imported_dict['starting_units']:
            coor_x = unit_dict['coor_x'] - 1
            coor_y = unit_dict['coor_y'] - 1
            unit_type = unit_dict['unit_type']
            side = unit_dict['side']
            piece: BasePiece = locate(f'pieces.{unit_type[:-5].lower()}.{unit_type}')(id=incremental_id)
            incremental_id += 1
            if side == 'black':
                piece.set_player(player=self.black)
            if side == 'white':
                piece.set_player(player=self.white)

            self.board[coor_x][coor_y] = piece

    # end __init__()

    def perform_move(self,
                     current_player: Player,
                     initial_position: Tuple[int, int],
                     final_position: Optional[Tuple[int, int]],
                     promote: bool):
        """
        Perform a move on the board.

        Arguments:
        - current_player (Player):
            The one making the move
        - initial_position (Tuple[int, int]):
            Coordinate of the initial position of a move
        - final_position (Optional[Tuple[int, int]]):
            Coordinate of the final position of a move
        - promote (bool):
            A value denotes if the piece would be promoted after the move or not
            (will be forced to be promoted if stuck afterwards)
        """
        if self.black is None:
            raise GameNotInitiatedError
        if self.winner is not None:
            raise GameEndedError
        if current_player != self.next_action:
            raise IncorrectPlayerError(
                attempted_player=current_player,
                actual_player=self.next_action
            )
        if not 0 <= initial_position[0] < self.dim \
           or not 0 <= initial_position[1] < self.dim:
            raise OutOfBoundError(initial_position)
        if not 0 <= final_position[0] < self.dim \
           or not 0 <= final_position[1] < self.dim:
            raise OutOfBoundError(final_position)

        if self.board[initial_position[0]][initial_position[1]] is None:
            raise EmptyCellError(coordinate=initial_position)

        if self.board[initial_position[0]][initial_position[1]].player != current_player:
            raise PieceNotOwnedError(
                coordinate=initial_position,
                attempted_player=current_player,
                actual_owner=~current_player
            )

        if promote and not self.board[initial_position[0]][initial_position[1]].promotable:
            raise NotPromotableError(
                piece_type=type(self.board[initial_position[0]][initial_position[1]]),
                coordinate=initial_position
            )

        if promote and (
            (current_player == self.black
             and not 0 <= initial_position[0] <= 2
             and not 0 <= final_position[0] <= 2)
            or
            (current_player == self.white
             and not self.dim-2 < initial_position[0] < self.dim
             and not self.dim-2 < final_position[0] < self.dim)
        ):
            raise NotInPromotionZoneError(
                initial_position=initial_position,
                final_position=final_position
            )

        try:
            if MovementUtils.is_valid_move(
                piece=self.board[initial_position[0]][initial_position[1]],
                board_black=self.black,
                board_dim=self.dim,
                board_matrix=self.board,
                initial_position=initial_position,
                final_position=final_position
            ):
                if self.board[final_position[0]][final_position[1]] is not None:
                    self.board[final_position[0]][final_position[1]].set_player(current_player)
                    self.captured_pieces[current_player].append(
                        self.board[final_position[0]][final_position[1]]
                    )

                self.board[final_position[0]][final_position[1]] = \
                    self.board[initial_position[0]][initial_position[1]]
                if InvalidDroppingUtils.check_for_stuck_piece(
                    piece=self.board[final_position[0]][final_position[1]],
                    board_black=self.black,
                    board_dim=self.dim,
                    position=final_position
                ):
                    if self.board[final_position[0]][final_position[1]].promotable:
                        self.board[final_position[0]][final_position[1]].promote()
                    else:
                        raise NotPromotableError(
                            piece_type=type(self.board[final_position[0]][final_position[1]]),
                            coordinate=final_position
                        )

                self.board[initial_position[0]][initial_position[1]] = None
                self.next_action = ~self.next_action
            else:
                raise Exception("An unknown error existed "
                                "that causes the checking function to return False")
        except GameplayException as gameplay_exception:
            logging.warning("An invalid move caused the game to end. "
                            f"Details:\n{repr(gameplay_exception)}")
            self.winner = ~current_player

    # end perform_move()

    def perform_drop(self,
                     piece: BasePiece,
                     current_player: Player,
                     position: Tuple[int, int]):
        """
        Perform a drop on the board.

        Arguments:
        - piece (BasePiece):
            The piece to be dropped
        - current_player (Player):
            The one making the drop
        - position (Tuple[int, int]):
            Coordinate of the dropping position
        """
        if self.black is None:
            raise GameNotInitiatedError
        if self.winner is not None:
            raise GameEndedError
        if current_player != self.next_action:
            raise IncorrectPlayerError(
                attempted_player=current_player,
                actual_player=self.next_action
            )
        if not 0 <= position[0] < self.dim \
           or not 0 <= position[1] < self.dim:
            raise OutOfBoundError(position)

        if self.board[position[0]][position[1]] is not None:
            raise OccupiedCellError(position)

        if piece not in self.captured_pieces[current_player]:
            raise DroppingPieceNotExistedError(piece_type=type(piece), piece_id=piece.id)

        try:
            if MovementUtils.is_valid_drop(
                piece=piece,
                board_black=self.black,
                board_dim=self.dim,
                board_matrix=self.board,
                drop_position=position,
                opponent_captured_pieces=self.captured_pieces[~current_player]
            ):
                self.board[position[0]][position[1]] = piece
                self.captured_pieces[current_player].remove(piece)
                self.next_action = ~self.next_action
            else:
                raise Exception("An unknown error existed "
                                "that causes the checking function to return False")
        except GameplayException as gameplay_exception:
            logging.warning("An invalid move caused the game to end. "
                            f"Details:\n{repr(gameplay_exception)}")
            self.winner = ~current_player

    # end perform_drop()

    def perform_action(self, action_dict: dict):
        """
        Perform an action on the board with the action specification dictionary

        Arguments:
        - action_dict (dict):
            The dictionary containing the action to be performed
        """
        side = action_dict.get('side') or side_symbols[(int(action_dict.get('action_no')) - 1) % 2]
        side = self.black if side_symbols.index(side) == 0 else self.white

        initial_position = None if action_dict.get('initial_position') is None \
                           else (
                                ord(action_dict.get('initial_position')[1]) - ord('1'),
                                ord(action_dict.get('initial_position')[2]) - ord('1')
                           )

        final_position = None if action_dict.get('final_position') is None \
                         else (
                            (full_arabic_nums.index(action_dict.get('final_position')[0])),
                            (full_kanji_nums.index(action_dict.get('final_position')[1]))
                         )

        piece = action_dict.get('piece')

        if action_dict.get('drop_promote') == drop_indicator:
            eligible_piece = None
            for candidate_piece in self.captured_pieces[side]:
                if candidate_piece.name_kanji_abbr_junior == piece \
                   or candidate_piece.name_kanji_abbr_senior == piece \
                   or candidate_piece.name_kanji_full_junior == piece \
                   or candidate_piece.name_kanji_full_senior == piece:
                    eligible_piece = candidate_piece
                    break
            self.perform_drop(
                piece=eligible_piece,
                current_player=side,
                position=final_position
            )
        else:
            self.perform_move(
                current_player=side,
                initial_position=initial_position,
                final_position=final_position,
                promote=action_dict.get('drop_promote') == promote_indicator
            )

    # end perform_action()

    @classmethod
    def create_from_kif(cls, first_move: Player, kif_path: str):
        """
        Create a board from an existing KIF file

        Arguments:
        - first_move (Player):
            Check if the black player is a junior or senior
        - kif_path (str):
            Path to the KIF file used for importing
        """
        board = cls(first_move=first_move)
        kif = Kif(kif_file=kif_path)
        for action_dict in kif.kif_dict['actions']:
            logging.info(f"Next action: {action_dict}")
            board.perform_action(action_dict=action_dict)

        return board

    # end create_from_kif()

    def __repr__(self):
        displaying_board = [
            [
                self.board[self.dim - 1 - index_y][index_x]
                for index_y in range(self.dim)
            ]
            for index_x in range(self.dim)
        ]

        string_matrix = [['＊' for _ in range(self.dim * 3 + 2)] for _ in range(self.dim * 3 + 2)]
        for index in range(len(string_matrix)):
            string_matrix[0][index] = '　'
            string_matrix[index][-1] = '　'
        for index in range(len(full_arabic_nums)):
            actual_index = index * 3 + 1 + 1
            string_matrix[0][actual_index] = full_arabic_nums[len(full_arabic_nums) - 1 - index]
        for index in range(len(full_kanji_nums)):
            actual_index = index * 3 + 2 + 1
            string_matrix[actual_index][-1] = full_kanji_nums[index]
        for index_x in range(self.dim):
            for index_y in range(self.dim):
                matrix_start_x = index_x * 3 + 2
                matrix_start_y = index_y * 3 + 1
                string_matrix[matrix_start_x+0][matrix_start_y+0] = '　'
                string_matrix[matrix_start_x+0][matrix_start_y+1] = '　'
                string_matrix[matrix_start_x+1][matrix_start_y+0] = '　'
                string_matrix[matrix_start_x+1][matrix_start_y+1] = '　'
                if displaying_board[index_x][index_y] is None:
                    continue
                string_matrix[matrix_start_x+0][matrix_start_y+1] = \
                    '↑↑' if displaying_board[index_x][index_y].player == self.black else '↓↓'
                string_matrix[matrix_start_x+1][matrix_start_y+0] = \
                    repr(displaying_board[index_x][index_y])[0]
                if len(repr(displaying_board[index_x][index_y])) > 1:
                    string_matrix[matrix_start_x+1][matrix_start_y+1] = \
                        repr(displaying_board[index_x][index_y])[1]

        return '\n'.join(list(map(lambda chlist: ''.join(chlist), string_matrix)))

    # end __repr__()

# end ShogiBoard
