import re
import polars as pl
from core_pro.ultilities import make_sync_folder


def pattern():
    return {
        'quantity': 'cái|chiếc|miếng|tờ|quyển|hộp|set|bộ|gói|túi|kẹp|thùng|chai|lọ|túi|viên|cây|bao|lon|miếng|dây|lớp',
        'weight': 'kg|g|gram|ml|lít|gam|gram|cm|mm|m',
    }


def extract(item_name: str, pattern: str):
    """
    Extract quantity from Vietnamese item names.

    Args:
        item_name (str): The input item name string

    Returns:
        list: A list of detected quantity strings
    """
    patterns = [
        fr'\b((?:\d+(?:\.\d+)?)\s*(?:kg|g|gram|ml|lít|cm)?/?(?:{pattern}))\b'  # "1.8kg/gói", "70 kẹp", "1.8 gói
        fr'\b(\d+\s*(?:{pattern}))\b',  # "70 kẹp", "250 giấy", etc.
        fr'\b((?:\d+(?:\.\d+)?)\s*(?:{pattern}))\b',  # "1.8 gói"
        fr'\b(\d+\s*[-\s]\s*(?:{pattern}))\b',  # optional space between number and unit
    ]

    # Collect all matches
    key_lst = []
    for pattern in patterns:
        matches = re.findall(pattern, item_name, re.UNICODE | re.IGNORECASE)
        if matches:
            key_lst.extend(matches)

    return ', '.join(list(dict.fromkeys(key_lst)))


path = make_sync_folder('nlp/ner')
df = pl.read_parquet(path / 'ner_wishlist.parquet')

pattern_dict = pattern()
for i, v in pattern_dict.items():
    lst = [extract(str(item), v) for item in df['item_name']]
    df = df.with_columns(pl.Series(i, lst))
col = ['item_id', 'item_name'] + list(pattern_dict.keys())
check = df[col].unique(subset=col)
df.write_csv(path / 'ner_wishlist.csv')
