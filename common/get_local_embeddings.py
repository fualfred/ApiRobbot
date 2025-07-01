#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import os
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

load_dotenv()

os.environ["HUGGINGFACE_HUB_LOCAL_PATH_WORKAROUND"] = "1"


class LocalEmbedding:
    _embedding = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                cls._instance = super().__new__(cls)
                model_path_str = Path('../bge-small-zh-v1.5').resolve()
                cls._embedding = embedding_functions.SentenceTransformerEmbeddingFunction(str(model_path_str))
        return cls._instance

    def get_embedding(self):
        return self._embedding


#
# embeddings = LocalEmbedding().get_embedding()
# # # # print(embeddings.embed_documents(["你好", "世界"]))
# print(embeddings)
# Load model directly
# Use a pipeline as a high-level helper
# from transformers import pipeline
#
# pipe = pipeline("feature-extraction", model="BAAI/bge-small-zh-v1.5")
