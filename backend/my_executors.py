# %%
import torch
from transformers import BertModel, BertTokenizer
import re
from typing import Sequence, List, Dict, Tuple

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


# ==============================================================================
# Code within this section copied from jina/helloworld/fashion/my_executors.py
# Identical to jina/helloworld/chatbot/my_executors.py
# Simple indexer class and supporting functions.

class MyIndexer(Executor):
    @requests(on='/index')
    def fdjslka(self, docs, **kwargs):
        print(docs)

'''
class MyIndexer(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._docs = DocumentArrayMemmap(self.workspace + "/indexer")

    @requests(on="/index")
    def index(self, docs: "DocumentArray", **kwargs):
        self._docs.extend(docs)

    @requests(on=["/search", "/eval"])
    def search(self, docs: "DocumentArray", parameters: Dict, **kwargs):
        a = np.stack(docs.get_attributes("embedding"))
        b = np.stack(self._docs.get_attributes("embedding"))
        q_emb = _ext_A(_norm(a))
        d_emb = _ext_B(_norm(b))
        dists = _cosine(q_emb, d_emb)
        idx, dist = self._get_sorted_top_k(dists, int(parameters["top_k"]))
        for _q, _ids, _dists in zip(docs, idx, dist):
            for _id, _dist in zip(_ids, _dists):
                d = Document(self._docs[int(_id)], copy=True)
                d.scores["cosine"] = 1 - _dist
                _q.matches.append(d)

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


# ==============================================================================
'''
