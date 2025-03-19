from src.model_train.func import upload_model_to_hub


path = "/media/kevin/data_4t/dataset/category_tag/model_multi_classes/label_vietnamese-bi-encoder/20250319132623"
upload_model_to_hub(folder=path, repo="kevinkhang2909/l2_category")


path = "/media/kevin/data_4t/dataset/category_tag/model_multi_classes/vietnamese-bi-encoder/20250318150616"
upload_model_to_hub(folder=path, repo="kevinkhang2909/l1_category")
