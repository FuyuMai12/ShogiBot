import re
from typing import Tuple

headers_mapping = {
    '手合割': 'handicap',
    '開始日時': 'start_date',
    '対局日': 'start_date',
    '終了日時': 'end_date',
    '棋戦': 'tournament',
    '戦型': 'opening',
    '表題': 'heading',
    '持ち時間': 'time_control',
    '消費時間': 'time_expended',
    '場所': 'location',
    '掲載': 'published',
    '備考': 'reference',
    '先手省略名': 'black_name',
    '先手': 'black_name',
    '後手省略名': 'white_name',
    '後手': 'white_name',
    '作品番号': 'problem_id',
    '作品名': 'problem_name',
    '作者': 'composer',
    '発表誌': 'publication',
    '発表年月': 'publication_date',
    '出典': 'collection',
    '手数': 'length',
    '完全性': 'status',
    '分類': 'type',
    '受賞': 'prize',
    '備考': 'reference'
}
movelist_indication = '手数----指手---------消費時間--'
separator_symbol = '：'
side_symbols = '▲△'
full_arabic_nums = '１２３４５６７８９'
full_kanji_nums = '一二三四五六七八九'
repeat_destination = '同　'
piece_types = ['玉', '飛', '龍', '竜', '角', '馬', '金', '銀',
               '成銀', '全', '桂', '成桂', '圭', '香', '成香', '杏', '歩', 'と']
drop_indicator = '打'
promote_indicator = '成'

def format_coordinates(coordinate: Tuple[int, int]):
    """
    Convert the technical coordinate tuple into the tuple format
    compatible with kifu / shogi notations

    Returns:
        str: A string of the new notation
    """
    return full_arabic_nums[coordinate[0]] + full_kanji_nums[coordinate[1]]

class Kif:
    """
    Structured KIF file wrapper for this project
    """
    def __init__(self, kif_file: str = None):
        kif_dict = self.__kif_to_dict(filename=kif_file)
        self.kif_dict = kif_dict

    def __kif_to_dict(self, filename: str = None):
        kif_content = open(filename, "r", encoding="utf-8").readlines()
        content_dict = {}
        regex_move_pattern = f"([{side_symbols}])?" \
                             f"((?:[{full_arabic_nums}][{full_kanji_nums}])|{repeat_destination})" \
                             f"({'|'.join(piece_types)})" \
                             f"([{drop_indicator}{promote_indicator}])?" \
                             f"(\\((?:[1-9])(?:[1-9])\\))?"

        for line in kif_content:
            line_without_comment = re.match(r"([^#]*)( *#.*)?", line.strip()).group(1)
            if separator_symbol in line_without_comment:
                header, value = line_without_comment.split(separator_symbol)
                content_dict[headers_mapping[header]] = value
            elif line_without_comment == movelist_indication:
                content_dict['actions'] = []
            elif 'actions' in content_dict:
                try:
                    action_no, action_details, action_time = re.split(' +', line_without_comment)
                    regex_groups = re.match(regex_move_pattern, action_details)
                    if regex_groups is not None:
                        content_dict['actions'].append({
                            'action_no': action_no,
                            'action_time': action_time,
                            'side': regex_groups.group(1),
                            'final_position': regex_groups.group(2) if regex_groups.group(2) != repeat_destination
                                              else content_dict['actions'][-1]['final_position'],
                            'piece': regex_groups.group(3),
                            'drop_promote': regex_groups.group(4),
                            'initial_position': regex_groups.group(5)
                        })
                except Exception:
                    content_dict['verdict'] = line_without_comment
            else:
                pass

        return content_dict


if __name__ == '__main__':
    kif_path = 'games/81Dojo-2211162159-DaimyoTuruu-phuctuyen.kif'
    kif = Kif(kif_file=kif_path)
    print('\n'.join(map(str, kif.kif_dict['actions'])))