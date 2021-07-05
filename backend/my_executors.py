#%%
import torch
from transformers import BertModel, BertTokenizer
import re

from jina import Executor, requests
from jina import Document, DocumentArray

class ProtBertExecutor(Executor):
    def __init__(self, **kwargs):
        super().__init__()

        tokenizer = BertTokenizer.from_pretrained("Rostlab/prot_bert", do_lower_case=False )
        model = BertModel.from_pretrained("Rostlab/prot_bert")

        self.tokenizer = tokenizer
        self.model = model


    @requests
    def encode(self, docs, **kwargs):
        sequences = docs.get_attributes('text')
        sequences = [re.sub(r"[UZOB]", "X", seq) for seq in sequences]

        encoded_inputs = self.tokenizer(sequences, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**encoded_inputs)
            embeds = outputs.last_hidden_state[:, 0, :].detach().numpy()
            for doc, embed in zip(docs, embeds):
                doc.embedding = embed

        return docs
#%%
sequences = ["A E T C Z A O", "T E A B Z A O"]
sequences = [re.sub(r"[UZOB]", "X", seq) for seq in sequences]

docs = DocumentArray((Document(content=seq) for seq in sequences))

#%%
embedded_docs = ProtBertExecutor().encode(docs)
# %%
