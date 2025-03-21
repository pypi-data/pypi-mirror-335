import json
from typing import List
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader


class QAJSONLoader(BaseLoader):
    """Load local `{"question":"","answer":"","meta_key":""}` json files."""

    def __init__(self, file_path: str):
        """Initialize with a file path. This should start with '/tmp/airbyte_local/'."""
        self.file_path = file_path
        """Path to the directory containing the json files."""

    def load(self) -> List[Document]:
        res = []
        for line in open(self.file_path, "r"):
            data = json.loads(line)
            if data["question"]:
                meta_key = data["meta_key"] or "answer"
                res.append(Document(page_content=data["question"], metadata={"source": self.file_path,
                                                                             meta_key: data["answer"]}))
        return res
