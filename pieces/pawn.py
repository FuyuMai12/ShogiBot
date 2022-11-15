from pieces.base import BasePiece

default_profile_path = "profiles/pieces/pawn.json"


class PawnPiece(BasePiece):
    """
    Class for a Pawn piece.

    Inherits: BasePiece
    """
    def __init__(self, id: int):
        base = BasePiece.create_from_json_profile(id=id, json_file=default_profile_path)
        super().__init__(
            id=base.id,
            name_en=base.name_en,
            name_vi=base.name_vi,
            name_hv_senior=base.name_hv_senior,
            name_hv_junior=base.name_hv_junior,
            name_kanji_full_senior=base.name_kanji_full_senior,
            name_kanji_full_junior=base.name_kanji_full_junior,
            name_kanji_abbr_senior=base.name_kanji_abbr_senior,
            name_kanji_abbr_junior=base.name_kanji_abbr_junior,
            name_en_abbr=base.name_en_abbr,
            name_vi_abbr=base.name_vi_abbr,
            promotable=base.promotable,
            promoted_name_en=base.promoted_name_en,
            promoted_name_vi=base.promoted_name_vi,
            promoted_name_hv_senior=base.promoted_name_hv_senior,
            promoted_name_hv_junior=base.promoted_name_hv_junior,
            promoted_name_kanji_full_senior=base.promoted_name_kanji_full_senior,
            promoted_name_kanji_full_junior=base.promoted_name_kanji_full_junior,
            promoted_name_kanji_abbr_senior=base.promoted_name_kanji_abbr_senior,
            promoted_name_kanji_abbr_junior=base.promoted_name_kanji_abbr_junior,
            promoted_name_en_abbr=base.promoted_name_en_abbr,
            promoted_name_vi_abbr=base.promoted_name_vi_abbr
        )

    # end __init__()

# end PawnPiece
