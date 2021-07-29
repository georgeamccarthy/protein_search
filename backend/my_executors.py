import torch
import re
import os
import numpy as np

from typing import Sequence, List, Tuple
from transformers import BertModel, BertTokenizer
from jina import Executor, requests, Document, DocumentArray

from backend_config import top_k, embeddings_path, results_path
from utils import partition
from helpers import log


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

    # All requests to ProtBertExecutor run encode()
    @requests
    def encode(
        self, docs: DocumentArray, batch_size: int = 10000, **kwargs
    ) -> DocumentArray:
        log('Indexing.')

        log('Batchifying.')
        batches = self.batchify(docs, batch_size)

        for batch_num, docs_batch in enumerate(batches):
            log(f'Encoding batch {batch_num+1}/{np.ceil(len(docs)/batch_size):.0f}.')
            self.encode_batch(docs_batch)

        log('Indexing completed.')
        return docs

    def encode_batch(self, docs: DocumentArray, **kwargs) -> DocumentArray:

        log('Preprocessing.')
        sequences = self.preprocessing(docs.get_attributes("text"))

        log('Tokenizing')
        encoded_inputs = self.tokenizer(
            sequences,
            padding=True,
            max_length=max(sequences, key=len),
            return_tensors="pt",
        )

        with torch.no_grad():
            log('Computing embeddings.')
            outputs = self.model(**encoded_inputs)
            log('Getting last hidden state.')
            embeds = outputs.last_hidden_state[:, 0, :].detach().numpy()
            for doc, embed in zip(docs, embeds):
                log(f'Getting embedding {doc.id}')
                doc.embedding = embed

        return docs

    def batchify(self, docs: DocumentArray, batch_size: int) -> List[DocumentArray]:
        docs.sort(key=lambda doc: len(doc.text))

        return partition(docs, batch_size)

    def format_sequence(self, seq: str):
        # TODO: add some checks and format different cases?
        seq = seq.upper()
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

    @requests(on="/index")
    def index(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)
        self.save()
        return docs

    @requests(on="/search")
    def search(self, docs: "DocumentArray", **kwargs):
        docs.match(self._docs, metric='cosine', limit=top_k)
        return docs

    def save(self):
        if not os.path.exists('embeddings'):
            os.mkdir('embeddings')
        self._docs.save(embeddings_path)
