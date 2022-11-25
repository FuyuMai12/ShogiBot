from typing import List, Tuple

from boards.board import ShogiBoard
from const.gameplay import Player
from models.genalgo.base import ShogiGeneticAlgorithmBaseBot
from pieces.bishop import BishopPiece
from pieces.gold import GoldPiece
from pieces.king import KingPiece
from pieces.knight import KnightPiece
from pieces.lance import LancePiece
from pieces.pawn import PawnPiece
from pieces.rook import RookPiece
from pieces.silver import SilverPiece
from util.board import MovementUtils
from util.kif import drop_indicator, full_arabic_nums, full_kanji_nums, promote_indicator, side_symbols


possible_cells = [
    None, "P", "+P",
    "L", "+L", "N", "+N", "S", "+S", "G",
    "B", "+B", "R", "+R", "K"
]

status_mapping = {
    (PawnPiece, False): "P",
    (PawnPiece, True): "+P",
    (LancePiece, False): "L",
    (LancePiece, True): "+L",
    (KnightPiece, False): "N",
    (KnightPiece, True): "+N",
    (SilverPiece, False): "S",
    (SilverPiece, True): "+S",
    (GoldPiece, False): "G",
    (BishopPiece, False): "B",
    (BishopPiece, True): "+B",
    (RookPiece, False): "R",
    (RookPiece, True): "+R",
    (KingPiece, False): "K"
}

kanji_mapping = {
    (PawnPiece, False): "歩",
    (PawnPiece, True): "と",
    (LancePiece, False): "香",
    (LancePiece, True): "成香",
    (KnightPiece, False): "桂",
    (KnightPiece, True): "成桂",
    (SilverPiece, False): "銀",
    (SilverPiece, True): "成銀",
    (GoldPiece, False): "金",
    (BishopPiece, False): "角",
    (BishopPiece, True): "馬",
    (RookPiece, False): "飛",
    (RookPiece, True): "龍",
    (KingPiece, False): "玉"
}


class ShogiGeneticAlgorithmBotV1(ShogiGeneticAlgorithmBaseBot):
    def __init__(self, seed: int = 21212,
                 value_lower: float = -10.0,
                 value_upper: float = 10.0):
        """
        Constructor

        Arguments:
        - seed (int):
            Seed of the bot's RNG
        - value_lower (float):
            Lower bound value of a gene
        - value_upper (float):
            Upper bound value of a gene
        """
        gene_names = []
        for curr_x in range(9):
            for curr_y in range(9):
                for targ_x in range(9):
                    for targ_y in range(9):
                        for curr_status in possible_cells[1:]:
                            for targ_status in possible_cells:
                                gene_names.append(f"onboard_{curr_x+1}{curr_y+1}{curr_status}"
                                                  f"_{targ_x+1}{targ_y+1}{targ_status}")
                                if targ_status is not None:
                                    gene_names.append(f"onboard_{curr_x+1}{curr_y+1}{curr_status}"
                                                      f"_{targ_x+1}{targ_y+1}{targ_status}_ally")
        for piece in possible_cells[1:]:
            gene_names.append(f"captured_{piece}")

        super().__init__(seed=seed,
                         value_lower=value_lower,
                         value_upper=value_upper,
                         gene_names=gene_names)

        self.onboard_influence_matrix = [
            [
                [
                    [
                        {
                            curr_status: {
                                targ_status:
                                    self.genes[f"onboard_{curr_x+1}{curr_y+1}{curr_status}"
                                               f"_{targ_x+1}{targ_y+1}{targ_status}"]
                                for targ_status in possible_cells
                            }
                            for curr_status in possible_cells[1:]
                        }
                        for targ_y in range(9)
                    ]
                    for targ_x in range(9)
                ]
                for curr_y in range(9)
            ]
            for curr_x in range(9)
        ]

        self.onboard_allied_influence_matrix = [
            [
                [
                    [
                        {
                            curr_status: {
                                targ_status:
                                    self.genes[f"onboard_{curr_x+1}{curr_y+1}{curr_status}"
                                               f"_{targ_x+1}{targ_y+1}{targ_status}_ally"]
                                for targ_status in possible_cells[1:]
                            }
                            for curr_status in possible_cells[1:]
                        }
                        for targ_y in range(9)
                    ]
                    for targ_x in range(9)
                ]
                for curr_y in range(9)
            ]
            for curr_x in range(9)
        ]

        self.captured_influence_vector = {
            piece: self.genes[f"captured_{piece}"]
            for piece in possible_cells[1:]
        }

    # end __init__()

    def __cell_value(self, bot_side: Player, board: ShogiBoard,
                     coordinates: Tuple[int, int]) -> float:
        """
        Return a cell's value/advantage based on the current player

        Arguments:
        - bot_side (Player):
            The side the bot is in
        - board (ShogiBoard):
            The current shogi board
        - coordinates (Tuple[int, int]):
            The coordinates being considered

        Returns:
            float:
                A value denoting the advantage value of the cell for the current player
        """
        total_value = 0

        curr_x, curr_y = coordinates
        curr_status = status_mapping[(
            type(board.board[curr_x][curr_y]),
            board.board[curr_x][curr_y].is_promoted
        )]

        for targ_x in range(board.dim):
            for targ_y in range(board.dim):
                if curr_x == targ_x and curr_y == targ_y:
                    continue
                if board.board[targ_x][targ_y] is None:
                    total_value += self.onboard_influence_matrix\
                        [curr_x][curr_y][targ_x][targ_y][curr_status][None]
                    continue
                targ_status = status_mapping.get((
                    type(board.board[targ_x][targ_y]),
                    board.board[targ_x][targ_y].is_promoted
                ))
                if board.board[targ_x][targ_y].player == bot_side:
                    total_value += self.onboard_allied_influence_matrix\
                        [curr_x][curr_y][targ_x][targ_y][curr_status][targ_status]
                    total_value += self.onboard_allied_influence_matrix\
                        [targ_x][targ_y][curr_x][curr_y][targ_status][curr_status]
                else:
                    total_value += self.onboard_influence_matrix\
                        [curr_x][curr_y][targ_x][targ_y][curr_status][targ_status]

        return total_value

    # end __board_value()

    def possible_actions(self, bot_side: Player, board: ShogiBoard) -> List[Tuple[dict, float]]:
        """
        List the possible actions of the bot given the current board

        Arguments:
        - bot_side (Player): the side the bot is in
        - board (ShogiBoard): the current shogi board

        Returns:
            List[Tuple[dict, float]]:
                A list of possible actions (in the form of a dict) and the according value/advantage
                that action added to the bot (that value could be negative, of course).
        """
        actions = []

        occupied_cells = []
        empty_cells = []
        for curr_x in range(board.dim):
            for curr_y in range(board.dim):
                if board.board[curr_x][curr_y] is None:
                    empty_cells.append((curr_x, curr_y))
                    continue
                if board.board[curr_x][curr_y].player == bot_side:
                    occupied_cells.append((curr_x, curr_y))

        pov_coefficient = -1 if bot_side == board.black else 1
        for curr_x, curr_y in occupied_cells:
            piece = board.board[curr_x][curr_y].copy()
            for baseline in piece.moves_in_use:
                step = 1
                while True:
                    if step > 1 and baseline.step_limit is True:
                        break
                    targ_x = curr_x + baseline.x_per_step * step * pov_coefficient
                    targ_y = curr_y + baseline.y_per_step * step * pov_coefficient
                    if not 0 <= targ_x < board.dim:
                        break
                    if not 0 <= targ_y < board.dim:
                        break
                    if MovementUtils.is_blocked(
                        piece=piece,
                        position=(curr_x, curr_y),
                        board_black=board.black,
                        board_dim=board.dim,
                        board_matrix=board.board,
                        baseline=baseline,
                        step=step
                    ):
                        break

                    value_change = 0
                    old_curr = board.board[curr_x][curr_y].copy() \
                               if board.board[curr_x][curr_y] is not None else None
                    old_targ = board.board[targ_x][targ_y].copy() \
                               if board.board[targ_x][targ_y] is not None else None
                    board.board[curr_x][curr_y] = None
                    board.board[targ_x][targ_y] = piece
                    value_change += self.__cell_value(bot_side, board, (targ_x, targ_y))
                    board.board[curr_x][curr_y] = old_curr
                    board.board[targ_x][targ_y] = old_targ
                    value_change -= self.__cell_value(bot_side, board, (curr_x, curr_y))
                    action_dict = {
                        'side': side_symbols[0] if bot_side == board.black else side_symbols[1],
                        'final_position': f'{full_arabic_nums[targ_x]}{full_kanji_nums[targ_y]}',
                        'piece': kanji_mapping[(type(piece), piece.is_promoted)],
                        'initial_position': f'({curr_x+1}{curr_y+1})'
                    }
                    actions.append((action_dict ,value_change))

                    if MovementUtils.involving_promotion_zone(
                        board_black=board.black,
                        board_dim=board.dim,
                        attempting_player=bot_side,
                        initial_position=(curr_x, curr_y),
                        final_position=(targ_x, targ_y)
                    ) and piece.promotable and not piece.is_promoted:
                        value_change = 0
                        old_curr = board.board[curr_x][curr_y].copy() \
                                   if board.board[curr_x][curr_y] is not None else None
                        old_targ = board.board[targ_x][targ_y].copy() \
                                   if board.board[targ_x][targ_y] is not None else None
                        board.board[curr_x][curr_y] = None
                        board.board[targ_x][targ_y] = piece
                        board.board[targ_x][targ_y].promote()
                        value_change += self.__cell_value(bot_side, board, (targ_x, targ_y))
                        board.board[targ_x][targ_y].demote()
                        board.board[curr_x][curr_y] = old_curr
                        board.board[targ_x][targ_y] = old_targ
                        value_change -= self.__cell_value(bot_side, board, (curr_x, curr_y))
                        action_dict = {
                            'side': side_symbols[0] if bot_side == board.black else side_symbols[1],
                            'final_position': f'{full_arabic_nums[targ_x]}{full_kanji_nums[targ_y]}',
                            'piece': kanji_mapping[(type(piece), piece.is_promoted)],
                            'drop_promote': promote_indicator,
                            'initial_position': f'({curr_x+1}{curr_y+1})'
                        }
                        actions.append((action_dict ,value_change))

                    step += 1

        for curr_x, curr_y in empty_cells:
            candidates = [piece.copy() for piece in board.captured_pieces[bot_side]]
            for piece in candidates:
                try:
                    if MovementUtils.is_valid_drop(
                        piece=piece,
                        board_black=board.black,
                        board_dim=board.dim,
                        board_matrix=board.board,
                        drop_position=(curr_x, curr_y),
                        opponent_captured_pieces=board.captured_pieces[~bot_side]
                    ):
                        board.board[curr_x][curr_y] = piece
                        board.captured_pieces[bot_side].remove(piece)
                        value_change = self.__cell_value(bot_side, board, (curr_x, curr_y))
                        board.captured_pieces[bot_side].append(piece)
                        board.board[curr_x][curr_y] = None
                        action_dict = {
                            'side': side_symbols[0] if bot_side == board.black else side_symbols[1],
                            'final_position': f'{full_arabic_nums[curr_x]}{full_kanji_nums[curr_y]}',
                            'piece': kanji_mapping[(type(piece), piece.is_promoted)],
                            'drop_promote': drop_indicator,
                        }
                        actions.append((action_dict ,value_change))
                except Exception:
                    continue

        return actions

    # end __possible_actions()

# end ShogiGeneticAlgorithmBotV1
