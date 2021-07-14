from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow
from my_executors import ProtBertExecutor, MyIndexer
from backend_config import protein_path
from random import randint


def main():
    proteins = DocumentArray(
        from_csv(
            fp=open(protein_path),
            field_resolver={"Protein sequences": "text"},
        )
    )
    protein = proteins[randint(0, len(proteins)-1)]
    print(f'Searching with protein sequence:\n{protein.text}')

    flow = (
        Flow(port_expose=12345, protocol='http')
        .add(uses=ProtBertExecutor)
        .add(uses=MyIndexer)
    )
    with flow:
        flow.index(proteins)
        flow.block()


if __name__ == "__main__":
    main()
