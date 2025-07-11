import json
from pathlib import Path
from typing import Dict

import pdfplumber

PROCESSED_DIR = Path('processed_docs')
PDF_DIR = Path('pdf_docs')
METADATA_FILE = PROCESSED_DIR / 'metadata.json'


def load_metadata() -> Dict[str, Dict]:
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_metadata(meta: Dict[str, Dict]):
    PROCESSED_DIR.mkdir(exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def process_pdf(pdf_path: Path, meta: Dict[str, Dict]):
    mtime = pdf_path.stat().st_mtime
    if pdf_path.name in meta and meta[pdf_path.name]['mtime'] == mtime:
        return  # no changes
    text_file = PROCESSED_DIR / f'{pdf_path.stem}.txt'
    pages_text = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ''
            pages_text.append(f'<!-- p. {i} -->\n{text}\n<!-- /p. {i} -->')
    text_file.write_text('\n'.join(pages_text), encoding='utf-8')
    meta[pdf_path.name] = {
        'pages': len(pages_text),
        'mtime': mtime,
    }


def ingest_all():
    meta = load_metadata()
    for pdf in PDF_DIR.glob('*.pdf'):
        process_pdf(pdf, meta)
    save_metadata(meta)


if __name__ == '__main__':
    ingest_all()
