import torch
from transformers import BertModel, BertTokenizer
import re
from typing import Sequence, List, Dict, Tuple
import os
import numpy as np

from jina import Executor, requests
from jina import Document, DocumentArray
from backend_config import top_k, embeddings_path, results_path


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
        if os.path.exists(self.save_path):
            self._docs = DocumentArray.load(self.save_path)
        else:
            self._docs = DocumentArray()

    @requests(on="/index")
    def index(self, docs: "DocumentArray", **kwargs):
        self._docs = docs
        self.save()
        return docs

    @requests(on="/search")
    def search(self, docs: "DocumentArray", **kwargs):
        # Load proteins from csv.
        proteins = DocumentArray.load(self.save_path)
        results = DocumentArray()

        """Search method and called methods are as in the chatbot example"""
        a = np.stack(docs.get_attributes("embedding"))
        b = np.stack(proteins.get_attributes("embedding"))
        q_emb = _ext_A(_norm(a))
        d_emb = _ext_B(_norm(b))
        dists = _cosine(q_emb, d_emb)
        idx, dist = self._get_sorted_top_k(dists, top_k)
        for _q, _ids, _dists in zip(docs, idx, dist):
            for _id, _dist in zip(_ids, _dists):
                d = Document(self._docs[int(_id)], copy=True)
                d.scores["cosine"] = 1 - _dist
                _q.matches.append(d)
                results.append(d)

        self.save_results(results)

        return results

    @staticmethod
    def _get_sorted_top_k(
        dist: "np.array", top_k: int
    ) -> Tuple["np.ndarray", "np.ndarray"]:
        if top_k >= dist.shape[1]:
            idx = dist.argsort(axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx, axis=1)
        else:
            idx_ps = dist.argpartition(kth=top_k, axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx_ps, axis=1)
            idx_fs = dist.argsort(axis=1)
            idx = np.take_along_axis(idx_ps, idx_fs, axis=1)
            dist = np.take_along_axis(dist, idx_fs, axis=1)

        return idx, dist

    @property
    def save_path(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)

        return os.path.join(embeddings_path)

    def save(self):
        self._docs.save(self.save_path)

    def save_results(self, results):
        """Save search results in persistent file."""
        results.save(results_path)


def _get_ones(x, y):
    return np.ones((x, y))


def _ext_A(A):
    nA, dim = A.shape
    A_ext = _get_ones(nA, dim * 3)
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext


def _ext_B(B):
    nB, dim = B.shape
    B_ext = _get_ones(dim * 3, nB)
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext


def _euclidean(A_ext, B_ext):
    sqdist = A_ext.dot(B_ext).clip(min=0)
    return np.sqrt(sqdist)


def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)


def _cosine(A_norm_ext, B_norm_ext):
    return A_norm_ext.dot(B_norm_ext).clip(min=0) / 2
