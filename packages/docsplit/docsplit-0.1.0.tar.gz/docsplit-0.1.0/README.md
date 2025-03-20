# DocSplit

A Python package for document splitting and conversion

## Installation

```bash
pip install docsplit
```

## Usage

```python
from docsplit.handlers import DocumentSplitterHandler

handler = DocumentSplitterHandler()
payload = {
    'data': [{
        'doc_id': 'doc1',
        'doc_path': '/path/to/document.pdf',
        'split_format': 'jpg'
    }]
}

result = handler.split_documents(payload)
```
