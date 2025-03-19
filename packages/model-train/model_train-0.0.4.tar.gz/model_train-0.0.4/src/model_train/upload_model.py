from huggingface_hub import login, HfApi
from core_pro.ultilities import make_sync_folder
from transformers import AutoTokenizer


path = make_sync_folder('cx_product_review')
path_model = path / 'training_data/model_multi_labels_all/vietnamese-bi-encoder/20241115132902'
hf_token = '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'
login(token=hf_token)

tokenizer = AutoTokenizer.from_pretrained('bkai-foundation-models/vietnamese-bi-encoder')
tokenizer.save_pretrained(path_model)

repo = 'kevinkhang2909/product_review'
api = HfApi()
api.upload_folder(
    folder_path=path_model,
    repo_id=repo,
    commit_message='model updated',
    ignore_patterns=['checkpoint*']
)