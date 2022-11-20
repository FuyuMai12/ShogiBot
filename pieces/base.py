import json
import logging
from typing import List, Optional

from const.gameplay import Player


class MovementBaseline():
    """
    Class to define baseline for a Shogi piece's movement.
    One Shogi piece can have a number of valid baselines.
    """
    def __init__(self,
                 x_per_step: int,
                 y_per_step: int,
                 step_limit: bool,
                 bypass_pieces: bool):
        """
        Constructor.

        Arguments:
        - x_per_step (int):
            Number of cells in x axis per step that a piece could move using this baseline.
        - y_per_step (int):
            Number of cells in y axis per step that a piece could move using this baseline.
        - step_limit (bool):
            Check if with this baseline, a piece could move indefinitely or just 1 step.
        - bypass_pieces (bool):
            Check if with this baseline, a piece could move through any blocking pieces.
        """
        self.x_per_step: int = x_per_step
        self.y_per_step: int = y_per_step
        self.step_limit: bool = step_limit
        self.bypass_pieces: bool = bypass_pieces

    # end __init__()

    def __repr__(self):
        return str(vars(self))

    # end __repr__()

# end MovementBaseline


class BasePiece():
    """
    Base class for a Shogi piece
    """
    def __init__(self,
                 id: int,
                 name_en: str,
                 name_vi: str,
                 name_hv_senior: str,
                 name_hv_junior: Optional[str],
                 name_kanji_full_senior: str,
                 name_kanji_full_junior: Optional[str],
                 name_kanji_abbr_senior: str,
                 name_kanji_abbr_junior: Optional[str],
                 name_en_abbr: str,
                 name_vi_abbr: str,
                 promotable: bool,
                 promoted_name_en: Optional[str],
                 promoted_name_vi: Optional[str],
                 promoted_name_hv_senior: Optional[str],
                 promoted_name_hv_junior: Optional[str],
                 promoted_name_kanji_full_senior: Optional[str],
                 promoted_name_kanji_full_junior: Optional[str],
                 promoted_name_kanji_abbr_senior: Optional[str],
                 promoted_name_kanji_abbr_junior: Optional[str],
                 promoted_name_en_abbr: Optional[str],
                 promoted_name_vi_abbr: Optional[str],
                 moves: List[MovementBaseline],
                 promoted_moves: List[MovementBaseline]):
        """
        Constructor. Not recommended to use this. See the next method.

        Arguments:
        - id (int):
            Distinctive identifier number of the piece
        - name_en (str):
            Piece type's name in English
        - name_vi (str):
            Piece type's name in Vietnamese
        - name_hv_senior (str):
            Piece type's name in Hanji, transliterated to Vietnamese
            This is the default full name attribute for any piece type, and in the case of Kings,
            this is the full name for the senior player / challenged player.
        - name_hv_junior (Optional[str]):
            Piece type's name in Hanji, transliterated to Vietnamese
            This is only used for Kings, as the full name for the junior player / challenger.
            Other piece types should leave this field as None.
        - name_kanji_full_senior (str):
            Piece type's full name in Kanji
            This is the default full name attribute for any piece type, and in the case of Kings,
            this is the full name for the senior player / challenged player.
        - name_kanji_full_junior (Optional[str]):
            Piece type's full name in Kanji
            This is only used for Kings, as the full name for the junior player / challenger.
            Other piece types should leave this field as None.
        - name_kanji_abbr_senior (str):
            Piece type's abbreviation in Kanji
            This is the default abbreviation attribute for any piece type, and in the case of Kings,
            this is the abbreviation for the senior player / challenged player.
        - name_kanji_abbr_junior (Optional[str]):
            Piece type's abbreviation in Kanji
            This is only used for Kings, as the abbreviation for the junior player / challenger.
            Other piece types should leave this field as None.
        - name_en_abbr (str):
            Piece type's abbreviation in English
        - name_vi_abbr (str):
            Piece type's abbreviation in Vietnamese
        - promotable (bool):
            Check if the piece type is able to be promoted
        - promoted_name_en (Optional[str]):
            Promoted piece type's name in English
            Must be None if promotable=False
        - promoted_name_vi (Optional[str]):
            Piece type's name in Vietnamese
            Must be None if promotable=False
        - promoted_name_hv_senior (Optional[str]):
            Piece type's name in Hanji, transliterated to Vietnamese
            This is the default full name attribute for any piece type, and in the case of Kings,
            this is the full name for the senior player / challenged player.
            Must be None if promotable=False
        - promoted_name_hv_junior (Optional[str]):
            Piece type's name in Hanji, transliterated to Vietnamese
            This is only used for Kings, as the full name for the junior player / challenger.
            Other piece types should leave this field as None.
            Must be None if promotable=False
        - promoted_name_kanji_full_senior (Optional[str]):
            Piece type's full name in Kanji
            This is the default full name attribute for any piece type, and in the case of Kings,
            this is the full name for the senior player / challenged player.
            Must be None if promotable=False
        - promoted_name_kanji_full_junior (Optional[str]):
            Piece type's full name in Kanji
            This is only used for Kings, as the full name for the junior player / challenger.
            Other piece types should leave this field as None.
            Must be None if promotable=False
        - promoted_name_kanji_abbr_senior (Optional[str]):
            Piece type's abbreviation in Kanji
            This is the default abbreviation attribute for any piece type, and in the case of Kings,
            this is the abbreviation for the senior player / challenged player.
            Must be None if promotable=False
        - promoted_name_kanji_abbr_junior (Optional[str]):
            Piece type's abbreviation in Kanji
            This is only used for Kings, as the abbreviation for the junior player / challenger.
            Other piece types should leave this field as None.
            Must be None if promotable=False
        - promoted_name_en_abbr (Optional[str]):
            Piece type's abbreviation in English
            Must be None if promotable=False
        - promoted_name_vi_abbr (Optional[str]):
            Piece type's abbreviation in Vietnamese
            Must be None if promotable=False
        - moves (List[MovementBaseline]):
            A list of moves decleared for the piece in normal form
        - promoted_moves (List[MovementBaseline]):
            A list of moves decleared for the piece in promoted form
        """
        self.id = id

        # instantinating base attributes
        self.name_en: str = name_en
        self.name_vi: str = name_vi
        self.name_hv_senior: str = name_hv_senior
        self.name_hv_junior: Optional[str] = name_hv_junior
        self.name_kanji_full_senior: str = name_kanji_full_senior
        self.name_kanji_full_junior: Optional[str] = name_kanji_full_junior
        self.name_kanji_abbr_senior: str = name_kanji_abbr_senior
        self.name_kanji_abbr_junior: Optional[str] = name_kanji_abbr_junior
        self.name_en_abbr: str = name_en_abbr
        self.name_vi_abbr: str = name_vi_abbr

        # instantinating promoted attributes
        self.promoted_name_en: Optional[str] = promoted_name_en
        self.promoted_name_vi: Optional[str] = promoted_name_vi
        self.promoted_name_hv_senior: Optional[str] = promoted_name_hv_senior
        self.promoted_name_hv_junior: Optional[str] = promoted_name_hv_junior
        self.promoted_name_kanji_full_senior: Optional[str] = promoted_name_kanji_full_senior
        self.promoted_name_kanji_full_junior: Optional[str] = promoted_name_kanji_full_junior
        self.promoted_name_kanji_abbr_senior: Optional[str] = promoted_name_kanji_abbr_senior
        self.promoted_name_kanji_abbr_junior: Optional[str] = promoted_name_kanji_abbr_junior
        self.promoted_name_en_abbr: Optional[str] = promoted_name_en_abbr
        self.promoted_name_vi_abbr: Optional[str] = promoted_name_vi_abbr

        # instantinating moveset attributes
        self.promotable: bool = promotable
        self.is_promoted: bool = False
        self.moves: List[MovementBaseline] = moves
        self.promoted_moves: List[MovementBaseline] = promoted_moves
        self.moves_in_use: List[MovementBaseline] = self.moves

        # attribute to check for junior(challenger)/senior(challengee) status
        self.player: Player = None

    # end __init__()

    @classmethod
    def create_from_json_profile(cls, id: int, json_file: Optional[str] = None):
        """
        Class method.
        Create an instance of BasePiece from a JSON profile file.
        The code for this is pretty strict and sensitive to error, thus the default
        JSON profile files shouldn't be modified recklessly.

        Arguments:
        - id:
            Defined identifier number for the created piece
        - json_file:
            Path to the JSON profile file.
        """
        file = open(json_file, 'r', encoding='utf-8')
        imported_dict = json.load(file)
        moves, promoted_moves = [], []
        for baseline_dict in imported_dict['moves']:
            moves.append(
                MovementBaseline(
                    x_per_step=baseline_dict['x_per_step'],
                    y_per_step=baseline_dict['y_per_step'],
                    step_limit=baseline_dict['step_limit'],
                    bypass_pieces=baseline_dict['bypass_pieces']
                )
            )
        for baseline_dict in imported_dict['promoted_moves']:
            promoted_moves.append(
                MovementBaseline(
                    x_per_step=baseline_dict['x_per_step'],
                    y_per_step=baseline_dict['y_per_step'],
                    step_limit=baseline_dict['step_limit'],
                    bypass_pieces=baseline_dict['bypass_pieces']
                )
            )
        base_piece = cls(
            id=id,
            name_en=imported_dict['name_en'],
            name_vi=imported_dict['name_vi'],
            name_hv_senior=imported_dict['name_hv_senior'],
            name_hv_junior=imported_dict['name_hv_junior'],
            name_kanji_full_senior=imported_dict['name_kanji_full_senior'],
            name_kanji_full_junior=imported_dict['name_kanji_full_junior'],
            name_kanji_abbr_senior=imported_dict['name_kanji_abbr_senior'],
            name_kanji_abbr_junior=imported_dict['name_kanji_abbr_junior'],
            name_en_abbr=imported_dict['name_en_abbr'],
            name_vi_abbr=imported_dict['name_vi_abbr'],
            promotable=imported_dict['promotable'],
            promoted_name_en=imported_dict['promoted_name_en'],
            promoted_name_vi=imported_dict['promoted_name_vi'],
            promoted_name_hv_senior=imported_dict['promoted_name_hv_senior'],
            promoted_name_hv_junior=imported_dict['promoted_name_hv_junior'],
            promoted_name_kanji_full_senior=imported_dict['promoted_name_kanji_full_senior'],
            promoted_name_kanji_full_junior=imported_dict['promoted_name_kanji_full_junior'],
            promoted_name_kanji_abbr_senior=imported_dict['promoted_name_kanji_abbr_senior'],
            promoted_name_kanji_abbr_junior=imported_dict['promoted_name_kanji_abbr_junior'],
            promoted_name_en_abbr=imported_dict['promoted_name_en_abbr'],
            promoted_name_vi_abbr=imported_dict['promoted_name_vi_abbr'],
            moves=moves,
            promoted_moves=promoted_moves,
        )
        return base_piece

    # end create_from_json_profile()

    def promote(self):
        """
        Promote the piece. Only when promotable=True
        """
        if self.promotable:
            if self.is_promoted:
                logging.info(f"This <{type(self)}> piece is already promoted.")
            else:
                self.is_promoted = True
                self.moves_in_use = self.promoted_moves
        else:
            logging.error(f"This <{type(self)}> piece does not have a promoted form!")

    # end promote()

    def demote(self):
        """
        Demote the piece. This is only a technical method used when the piece is captured.
        In a real Shogi game, a piece can't be demoted on board.
        """
        if self.is_promoted:
            self.is_promoted = False
            self.moves_in_use = self.moves
        else:
            logging.info(f"This <{type(self)}> piece is currently not promoted.")

    # end demote()

    def set_player(self, player: Player):
        """
        Set player state for this piece.
        """
        self.player = player

    def reset_player(self):
        """
        Remove player state for this piece.
        """
        self.player = None

    def __repr__(self):
        kanji = None
        if self.is_promoted:
            kanji = self.promoted_name_kanji_abbr_senior
            if self.player == Player.Junior and self.promoted_name_kanji_abbr_junior is not None:
                kanji = self.promoted_name_kanji_abbr_junior
        else:
            kanji = self.name_kanji_abbr_senior
            if self.player == Player.Junior and self.name_kanji_abbr_junior is not None:
                kanji = self.name_kanji_abbr_junior

        return kanji

    # end __repr__()

    def __eq__(self, other):
        return self.id == other.id

    # end __eq__()

    def __ne__(self, other):
        return self.id != other.id

    # end __ne__()

    def __lt__(self, other):
        return self.id < other.id

    # end __lt__()

    def __gt__(self, other):
        return self.id > other.id

    # end __gt__()

    def __le__(self, other):
        return self.id <= other.id

    # end __le__()

    def __ge__(self, other):
        return self.id >= other.id

    # end __ge__()

# end BasePiece
