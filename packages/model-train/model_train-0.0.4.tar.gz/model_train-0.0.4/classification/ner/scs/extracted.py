import re
from core_pro import Sheet
from core_pro.ultilities import make_sync_folder, update_df
import polars as pl
from tqdm import tqdm


sh = '1dJDgGZ8yuqIdhzwc6f1XMov9wflqvsVCwyCDg237_OU'
path = make_sync_folder('scs/brand')
# Sheet(sh).get_list_sheets()
# df_brand = Sheet(sh).google_sheet_into_df('[4] Brands to exclude', 'A:J')

df_brand = pl.read_csv(path / 'brand.csv')
df = pl.read_parquet(path / 'lst.parquet')
print(df.shape)
sample = df.filter(typical_model_id=215083606181)
lst_brand = sorted(df_brand['brand_name'].unique().to_list())


def find_keywords_l1(item_name, keywords):
    """
    Find all whole-word keywords in an item name, ignoring case.

    Args:
        item_name (str): The item name to search in
        keywords (list): List of keywords to search for

    Returns:
        list: Found keywords in their original form from the text
    """
    # Convert keywords to regex pattern with word boundaries
    pattern = '|'.join(r'\b' + re.escape(keyword) + r'\b' for keyword in keywords)

    # Find all matches, ignoring case
    matches = re.finditer(pattern, item_name, re.IGNORECASE)

    # Extract the actual matched text from the item name
    found_keywords = [item_name[match.start():match.end()] for match in matches]

    return found_keywords


def find_keywords_l2(item_name, keywords):
    """
    Find all whole-word keywords in an item name, ignoring case.

    Args:
        item_name (str): The item name to search in
        keywords (list): List of keywords to search for

    Returns:
        list: Found keywords in their original form from the text
    """
    # Define word separators: spaces, punctuation, or string boundaries
    separators = r'(?:^|\s|[.,!?;"\'])'
    end_separators = r'(?=$|\s|[.,!?;"\'])'

    # Convert keywords to regex pattern with strict word boundaries
    pattern = '|'.join(
        f'{separators}({re.escape(keyword)}){end_separators}'
        for keyword in keywords
    )

    # Find all matches, ignoring case
    matches = re.finditer(pattern, item_name, re.IGNORECASE)

    # Extract the actual matched text from the item name
    found_keywords = [item_name[match.start():match.end()] for match in matches]

    return found_keywords

lst = []
for i in tqdm(df['item_name']):
    check = find_keywords_l1(str(i), lst_brand)
    lst.append(','.join(check))

df = (
    df.with_columns(pl.Series('check_1', lst))
    .filter(pl.col('check_1') != '')
)

lst = []
for i in tqdm(df['item_name']):
    check = find_keywords_l2(str(i), lst_brand)
    lst.append(','.join(check))

df = (
    df.with_columns(pl.Series('check_2', lst))
    .filter(pl.col('check_2') != '')
)

update_df(df, '[DS] check', sh)