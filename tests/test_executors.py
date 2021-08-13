# Make the application source reachable
import sys

sys.path.append("../")
sys.path.append("./backend/src/")

from executors import *
from jina import Document, DocumentArray

sequences = ["AETCZAO", "TEABZAO"]


def encode_sequences(sequences):
    docs = DocumentArray((Document(content=seq) for seq in sequences))
    embedded_docs = ProtBertExecutor().encode(docs)

    return embedded_docs


def test_ProtBERT_encoding():
    embedded_docs = encode_sequences(sequences)


def test_Indexer_indexing_samelength():
    embedded_docs = encode_sequences(sequences)

    # indexing
    indexed_docs = MyIndexer().index(embedded_docs)

def test_search():
    embedded_docs = encode_sequences(sequences)

    # indexing
    indexer = MyIndexer()
    indexer.index(embedded_docs)

    indexer.search(embedded_docs)

    return embedded_docs
