import torch
import re
import os
import numpy as np

from typing import Sequence, List, Tuple
from transformers import BertModel, BertTokenizer
from jina import Executor, requests, Document, DocumentArray

from backend_config import top_k, embeddings_path
from utils import generate_path, partition
from helpers import log


class ProtBertExecutor(Executor):
    """ProtBERT executor: https://huggingface.co/Rostlab/prot_bert"""

    __model = None

    __tokenizer = None

    def __init__(self, **kwargs):
        log("Initialising ProtBertExecutor.")
        super().__init__()

        self.model = ProtBertExecutor.__model
        self.tokenizer = ProtBertExecutor.__tokenizer

    @staticmethod
    def initialize_executor():

        # If the model is not already cached ...
        if not os.path.isdir("./models/prot_bert"):

            # First fetch from `https://huggingface.co/`

            # # Log cache, file size info to user
            print(
                "[ProtBertExecutor.initialize_executor] WARNING: Model cache not found - fetching "
                "from https://huggingface.co/Rostlab/prot_bert (~1.68 GBs)"
            )

            # # Fetching the model
            model = BertModel.from_pretrained("Rostlab/prot_bert")

            # # Log success on complete fetch
            print("[ProtBertExecutor.initialize_executor] SUCCESS: Model fetched successfully")

            # Saving to disk for cache mechanism

            # # Saving model
            model.save_pretrained("./models/prot_bert")

            # # Log success on successful save
            print(
                "[ProtBertExecutor.initialize_executor] SUCCESS: Model saved "
                "successfully to local"
            )

        # If the tokenizer is not already cached
        if not os.path.isdir("./tokenizers/prot_bert"):

            # First fetch from `https://huggingface.co/`

            # # Log cache, file size info to user
            print(
                "[ProtBertExecutor.initialize_executor] WARNING: Tokenizer cache not found "
                "- fetching from https://huggingface.co/Rostlab/prot_bert (~1 MBs)"
            )

            # # Fetching the tokenizer
            tokenizer = BertTokenizer.from_pretrained(
                "Rostlab/prot_bert", do_lower_case=False
            )

            # # Log success on complete fetch
            print("[ProtBertExecutor.initialize_executor] SUCCESS: Model fetched successfully")

            # Saving to disk for cache mechanism

            # # Saving model
            tokenizer.save_pretrained("./tokenizers/prot_bert")

            # # Log success on successful save
            print(
                "[ProtBertExecutor.initialize_executor] SUCCESS: Tokenizer saved "
                "successfully to local"
            )

        # Assign model from cache
        ProtBertExecutor.__model = BertModel.from_pretrained("./models/prot_bert")

        # Success logging
        print("[ProtBertExecutor.initialize_executor] SUCCESS: Loaded model from cache")

        # Assign tokenizer from cache
        ProtBertExecutor.__tokenizer = BertTokenizer.from_pretrained(
            "./tokenizers/prot_bert", do_lower_case=False
        )

        # Success logging
        print("[ProtBertExecutor.initialize_executor] SUCCESS: Loaded tokenizer from cache")

    # All requests to ProtBertExecutor run encode()
    @requests
    def encode(
        self, docs: DocumentArray, batch_size: int = 10000, **kwargs
    ) -> DocumentArray:
        log("Indexing.")

        log("Batchifying.")
        batches = self.batchify(docs, batch_size)

        for batch_num, docs_batch in enumerate(batches):
            log(f"Encoding batch {batch_num+1}/{len(docs)}.")
            self.encode_batch(docs_batch)

        log("Indexing completed.")
        return docs

    def encode_batch(self, docs: DocumentArray, **kwargs) -> DocumentArray:

        log("Preprocessing.")
        sequences = self.preprocessing(docs.get_attributes("text"))

        log("Tokenizing")
        encoded_inputs = self.tokenizer(
            sequences,
            padding=True,
            max_length=max(sequences, key=len),
            return_tensors="pt",
        )

        with torch.no_grad():
            log("Computing embeddings.")
            outputs = self.model(**encoded_inputs)
            log("Getting last hidden state.")
            embeds = outputs.last_hidden_state[:, 0, :].detach().numpy()
            for doc, embed in zip(docs, embeds):
                log(f"Getting embedding {doc.id}")
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
    """Indexer Executor"""

    def __init__(self, **kwargs):
        log("Initialising Indexer.")
        super().__init__(**kwargs)
        if os.path.exists(embeddings_path):
            self._docs = DocumentArray().load(embeddings_path)
        else:
            self._docs = DocumentArray()

        log(f"Loaded {len(self._docs)} proteins with embeddings.")

    @requests(on="/index")
    def index(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)
        log("Saving embeddings.")
        self.save()
        return docs

    @requests(on="/search")
    def search(self, docs: "DocumentArray", **kwargs):
        log(f'Computing metric to {len(self._docs)} proteins.')

        docs.match(self._docs, metric='cosine', limit=top_k)

    def save(self):
        if not os.path.exists('embeddings'):
            os.mkdir('embeddings')
        self._docs.save(embeddings_path)
