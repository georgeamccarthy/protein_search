# %%
import torch
from transformers import BertModel, BertTokenizer
import re
from typing import Sequence, List

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


# %%
sequences = ["A E T C Z A O", "T E A B Z A O"]

docs = DocumentArray((Document(content=seq) for seq in sequences))

# %%
embedded_docs = ProtBertExecutor().encode(docs)