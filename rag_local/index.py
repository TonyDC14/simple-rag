from pathlib import Path
import re
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer

PROCESSED_DIR = Path('processed_docs')
COLLECTION_NAME = 'docs'
EMBED_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

model = SentenceTransformer(EMBED_MODEL_NAME)
client = QdrantClient(path='qdrant_data')


def read_pages(file: Path) -> List[Dict]:
    text = file.read_text(encoding='utf-8')
    pattern = re.compile(r'<!-- p\. (\d+) -->\n(.*?)\n<!-- /p\. \1 -->', re.S)
    pages = []
    for match in pattern.finditer(text):
        page_num = int(match.group(1))
        page_text = match.group(2).strip()
        pages.append({'page': page_num, 'text': page_text})
    return pages


def recreate_collection(dim: int):
    if COLLECTION_NAME in client.get_collections().collections:
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        COLLECTION_NAME,
        rest.VectorParams(size=dim, distance=rest.Distance.COSINE)
    )


def index_all():
    payloads = []
    vectors = []
    for txt in PROCESSED_DIR.glob('*.txt'):
        pages = read_pages(txt)
        for p in pages:
            payloads.append({'filename': f'{txt.stem}.pdf', 'page': p['page'], 'text': p['text']})
            vectors.append(model.encode(p['text']))
    if not vectors:
        return
    dim = len(vectors[0])
    recreate_collection(dim)
    client.upsert(collection_name=COLLECTION_NAME, points=[
        rest.PointStruct(id=i, vector=vectors[i], payload=payloads[i])
        for i in range(len(vectors))
    ])


if __name__ == '__main__':
    index_all()
