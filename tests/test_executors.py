# %% Make the application source reachable
import sys

sys.path.append("../")

# %%
from protein_search.backend.my_executors import *
from jina import DocumentArray, Flow
from jina.types.document.generators import from_csv

sequences = ["A E T C Z A O", "T E A B Z A O"]

def encode_sequences(sequences):
    docs = DocumentArray((Document(content=seq) for seq in sequences))
    embedded_docs = ProtBertExecutor().encode(docs)

    return embedded_docs


def test_ProtBERT_encoding():
    embedded_docs = encode_sequences(sequences)


if __name__ == "__main__":
    main()
