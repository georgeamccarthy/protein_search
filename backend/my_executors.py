# %%
import torch
from transformers import BertModel, BertTokenizer
import re
from typing import Sequence, List, Dict, Tuple
import os

from jina import Executor, requests
from jina import Document, DocumentArray

class ProtBertExecutor(Executor):
    """ProtBERT executor: https://huggingface.co/Rostlab/prot_bert"""

    def __init__(self, **kwargs):
        super().__init__()

        tokenizer = BertTokenizer.from_pretrained(
            "Rostlab/prot_bert", do_lower_case=False
        )
        model = BertModel.from_pretrained("Rostlab/prot_bert")

        self.tokenizer = tokenizer
        self.model = model

    @requests
    def encode(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        sequences = self.preprocessing(docs.get_attributes("text"))
        encoded_inputs = self.tokenizer(sequences, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**encoded_inputs)
            embeds = outputs.last_hidden_state[:, 0, :].detach().numpy()
            for doc, embed in zip(docs, embeds):
                doc.embedding = embed

        return docs

    def preprocessing(self, sequences: Sequence[str]) -> List[str]:
        """The rare amino acids "U,Z,O,B" are mapped to "X".

        :param sequences: a `Sequence` of proteins
        :return: a `List` of proteins with "U,Z,O,B" replaced by "X".
        """
        return [re.sub(r"[UZOB]", "X", seq) for seq in sequences]


class MyIndexer(Executor):
    """Indexer class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._docs = DocumentArray()
        self.top_k = 10
        if os.path.exists(self.save_path):
            self._docs = DocumentArray.load(self.save_path)
        else:
            self._docs = DocumentArray()

    @requests(on="/index")
    def index(self, docs: "DocumentArray", **kwargs):
        self._docs.extend(docs)
        self.save()
        return docs

    @property
    def save_path(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        return os.path.join("data/proteins.json")

    def save(self):
        self._docs.save(self.save_path)
