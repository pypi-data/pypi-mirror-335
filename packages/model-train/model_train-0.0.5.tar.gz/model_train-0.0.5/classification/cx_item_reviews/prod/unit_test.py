import duckdb
import polars as pl
from rich import print
from src.model_train.pipeline_infer import InferenceTextClassification
from classification.cx_item_reviews.prod.config import path_model

# init model
infer = InferenceTextClassification(
    path_model=str(path_model),
    col='comment',
    torch_compile=True,
    fp16=True
)

sample = 'Hồng vỏ đỗ mà ra cái màu hồng choé loé luôn. Choice ko uy tín gì cả. Sản phẩm phù hợp giá tiền'
result = infer.unit_test([sample])

labels = result['labels'][0]
scores = result['score'][0]

# Create a dictionary with label-score pairs
label_score_dict = {'label': labels, 'score': scores}

# Create the Polars DataFrame
df = pl.DataFrame(label_score_dict).to_pandas()