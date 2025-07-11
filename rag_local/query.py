from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer

from . import llm

COLLECTION_NAME = 'docs'
EMBED_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
model = SentenceTransformer(EMBED_MODEL_NAME)
client = QdrantClient(path='qdrant_data')


def search(query: str, k: int = 5):
    vector = model.encode(query)
    res = client.search(collection_name=COLLECTION_NAME, query_vector=vector, limit=k)
    return res


def build_prompt(question: str, hits) -> str:
    fragments = []
    refs = []
    for hit in hits:
        payload = hit.payload
        fragments.append(f"<!-- p. {payload['page']} -->\n{payload['text']}\n<!-- /p. {payload['page']} -->")
        refs.append(f"{payload['filename']} : {payload['page']}")
    context = '\n'.join(fragments)
    prompt = (
        "You are a helpful assistant. Answer the question using only the provided fragments.\n\n"
        f"{context}\n\nQuestion: {question}\nAnswer:" )
    return prompt, refs


def ask(question: str, provider: str = 'openai', k: int = 5):
    hits = search(question, k)
    prompt, refs = build_prompt(question, hits)
    response = llm.call_llm(prompt, provider)
    return response, refs


if __name__ == '__main__':
    import sys
    question = ' '.join(sys.argv[1:])
    ans, refs = ask(question)
    print(ans)
    print('References:', refs)
