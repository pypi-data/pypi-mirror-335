from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder

query = f"""
select
    *
from dev_vnbi_bd.scs_local_wishlist_cspu_v3
"""
path = make_sync_folder('nlp/ner')
df = DataPipeLine(query).run_presto_to_df(save_path=path / 'ner_wishlist.parquet')
