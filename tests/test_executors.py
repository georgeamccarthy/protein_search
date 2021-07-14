# %% Make the application source reachable
import sys

sys.path.append("../")
sys.path.append("./backend/")

# %%
from my_executors import *
from jina import Document, DocumentArray

sequences = ["A E T C Z A O", "T E A B Z A O"]

def encode_sequences(sequences):
    docs = DocumentArray((Document(content=seq) for seq in sequences))
    embedded_docs = ProtBertExecutor().encode(docs)

    return embedded_docs


def test_ProtBERT_encoding():
    embedded_docs = encode_sequences(sequences)