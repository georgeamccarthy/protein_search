# %%
import torch
import re
import os

from typing import Sequence, List
from transformers import BertModel, BertTokenizer
from jina import Executor, requests, DocumentArray

from utils import partition


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
    def encode(
        self, docs: DocumentArray, batch_size: int = 10000, **kwargs
    ) -> DocumentArray:
        batches = self.batchify(docs, batch_size)

        for docs_batch in batches:
            self.encode_batch(docs_batch)

        return docs

    def encode_batch(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        sequences = self.preprocessing(docs.get_attributes("text"))
        encoded_inputs = self.tokenizer(
            sequences,
            padding=True,
            max_length=max(sequences, key=len),
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = self.model(**encoded_inputs)
            embeds = outputs.last_hidden_state[:, 0, :].detach().numpy()
            for doc, embed in zip(docs, embeds):
                doc.embedding = embed

        return docs

    def batchify(self, docs: DocumentArray, batch_size: int) -> List[DocumentArray]:
        docs.sort(key=lambda doc: len(doc.text))

        return partition(docs, batch_size)

    def format_sequence(self, seq: str):
        # TODO: add some checks and format different cases?
        seq = re.sub(r"[UZOB]", "X", seq)
        seq = seq.replace("", " ").strip()

        return seq

    def preprocessing(self, sequences: Sequence[str]) -> List[str]:
        """The rare amino acids "U,Z,O,B" are mapped to "X".

        :param sequences: a `Sequence` of proteins
        :return: a `List` of proteins with "U,Z,O,B" replaced by "X".
        """
        return [self.format_sequence(seq) for seq in sequences]


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
    def index(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)
        self.save()
        return docs

    @property
    def save_path(self):
        # TODO: load the path from a config file
        if not os.path.exists("embeddings"):
            os.makedirs("embeddings")
        return os.path.join("embeddings/proteins.json")

    def save(self):
        self._docs.save(self.save_path)
