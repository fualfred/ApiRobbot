#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading

from langchain_ollama.embeddings import OllamaEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()


class Embedding:
    _embedding = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                cls._instance = super().__new__(cls)
                cls._embedding = OllamaEmbeddings(model='nomic-embed-text:latest',
                                                  base_url=os.getenv("OLLAMA_BASE_URL"))
        return cls._instance

    def get_embedding(self):
        return self._embedding


# print(embeddings.embed_documents(["你好", "世界"]))
# print(embeddings)
