# %% Make the application source reachable
import sys

sys.path.append("../")

# %%
from protein_search.backend.my_executors import *

# %%
def test_ProtBERT_encoding():
    sequences = ["A E T C Z A O", "T E A B Z A O"]
    docs = DocumentArray((Document(content=seq) for seq in sequences))
    embedded_docs = ProtBertExecutor().encode(docs)
