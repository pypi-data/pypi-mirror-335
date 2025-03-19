from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from torch import nn
from functools import partial


class InferenceTextClassification:
    def __init__(
            self,
            pretrain_name: str,
            torch_compile: bool = False,
            fp16: bool = True,
            task_type: str = "multi_labels",
            max_length: int = 50,
            batch_size: int = 1000
    ):
        """
        Initialize inference pipeline for text classification.

        :param pretrain_name: folder or model name
        :param torch_compile: If True, use torch.compile
        :param fp16: If True, use bfloat16 precision
        :param task_type: "multi_labels" or "one_label"
        :param max_length: Max token length for inputs
        :param batch_size: Batch size for inference
        """
        self.pretrain_name = pretrain_name
        self.task_type = task_type
        self.fp16 = fp16
        self.torch_compile = torch_compile
        self.max_length = max_length
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model resources
        self.tokenizer, self.model, self.id2label = self._load_model()

        # Print summary info
        self._print_summary()

    def _print_summary(self):
        print(f"""
*** [Device Summary] ***
Torch version: {torch.__version__}
Device: {self.device}
CUDA: {torch.cuda.get_device_properties(self.device).name if self.device.type == 'cuda' else "CPU only"}
"FlashAttention available: {str(torch.backends.cuda.flash_sdp_enabled()) if self.device.type == 'cuda' else ""}

*** [Inference Summary] ***
FP16: {self.fp16}
Torch Compile: {self.torch_compile}
Model Name: {self.pretrain_name}
""")

    def _load_model(self):
        """Load and configure the model and tokenizer."""
        tokenizer = AutoTokenizer.from_pretrained(self.pretrain_name)

        # Configure model loading parameters
        config = {"pretrained_model_name_or_path": self.pretrain_name}
        if self.fp16 and self.device.type == 'cuda':
            config["torch_dtype"] = torch.bfloat16

        # Load model
        model = AutoModelForSequenceClassification.from_pretrained(**config).to(self.device)
        model.eval()

        # Apply torch compile if requested
        if self.torch_compile and torch.__version__ >= "2.0.0":
            model = torch.compile(model)

        # Get label mapping
        id2label = list(model.config.id2label.values())

        return tokenizer, model, id2label

    def process_batch(self, inputs, text_column=None):
        """
        Process a batch of texts.

        :param inputs: Text inputs or dataset batch
        :param text_column: Column name if inputs is a dataset batch
        :return: Dict with scores and labels
        """
        # Handle single text or dataset batch
        texts = inputs if text_column is None else inputs[text_column]

        # Tokenize inputs
        input_tokens = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.max_length
        ).to(self.device)

        # Run inference
        with torch.inference_mode():
            output = self.model(**input_tokens).logits
            output = nn.Softmax()(output)

            # Apply activation based on task type
            if self.task_type == "multi_labels":
                probs = output.half().cpu().detach().numpy().tolist()
                result = {
                    "score": probs,
                    "labels": [self.id2label for _ in range(len(probs))]
                }
            else:
                probs, indices = torch.max(output, dim=1)
                result = {
                    "score": probs.half().cpu().detach().numpy().tolist(),
                    "labels": [self.id2label[i] for i in indices.cpu().detach().numpy().tolist()]
                }

        return result

    def run_pipeline(self, dataset, text_column: str):
        """
        Run inference on a dataset.

        :param dataset: Dataset to process
        :param text_column: Column containing text to classify
        :return: Dataset with predictions
        """
        processor = partial(self.process_batch, text_column=text_column)

        return dataset.map(
            processor,
            batched=True,
            batch_size=self.batch_size,
        )
