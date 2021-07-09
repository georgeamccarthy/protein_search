from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow
from my_executors import ProtBertExecutor, MyIndexer

def main():
    proteins = DocumentArray(
        from_csv(
            fp=open("data/samelength.csv"),
            field_resolver={"Protein sequences": "text"},
        )
    )

    flow = Flow().add(uses=ProtBertExecutor).add(uses=MyIndexer)
    with flow:
        flow.index(proteins)
        flow.close()

if __name__ == "__main__":
    main()
