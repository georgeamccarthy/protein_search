# %% Make the application source reachable
import sys

sys.path.append("../")

# %%
from protein_search.backend.my_executors import *
from jina import DocumentArray, Flow
from jina.types.document.generators import from_csv

# %%
def test_ProtBERT_encoding():
    sequences = ["A E T C Z A O", "T E A B Z A O"]
    docs = DocumentArray((Document(content=seq) for seq in sequences))
    embedded_docs = ProtBertExecutor().encode(docs)

# %%
'''
def test_Indexer_indexing_samelength():
    proteins = DocumentArray(
        from_csv(
            fp=open("data/samelength.csv"),
            field_resolver={"Protein sequences": "text"},
        )
    )

    flow = Flow().add(uses=ProtBertExecutor).add(uses=MyIndexer)
    with flow:
        flow.post('/index', proteins, return_results=False)
        flow.close()
'''

if __name__ == "__main__":
    main()
