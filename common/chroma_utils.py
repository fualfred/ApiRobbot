#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_chroma import Chroma
from common.get_embeddings import Embedding
from config.settings import settings
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

if not os.path.exists(settings.VECTOR_STORE_DIR):
    os.mkdir(settings.VECTOR_STORE_DIR)


class ChromaUtils:
    def __init__(self, collection_name="fast_api_collection"):
        self.collection_name = collection_name
        self.embeddings = Embedding().get_embedding()
        self.persist_directory = settings.VECTOR_STORE_DIR

    def _vector_db(self):
        vector_db = Chroma(collection_name=self.collection_name, embedding_function=self.embeddings,
                           persist_directory=self.persist_directory)
        return vector_db

    def add_file(self, file_path, metadata=None):
        loader = TextLoader(file_path)
        documents = loader.load()
        vector_db = self._vector_db()
        text_spliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_spliter.split_documents(documents)
        if metadata:
            for split in splits:
                split.metadata = {**split.metadata, **metadata}
        return vector_db.add_documents(splits)

    def add_documents(self, documents, metadata=None):
        vector_db = self._vector_db()
        if metadata:
            for document in documents:
                document.metadata = {**document.metadata, **metadata}
        return vector_db.add_documents(documents)

    def delete_collection(self):
        self._vector_db().delete_collection()

    def retriever(self):
        return self._vector_db().as_retriever(search_kwargs={"k": 5})


if __name__ == '__main__':
    pass
    chroma_utils = ChromaUtils()
    # # chroma_utils.delete_collection()
    ids = chroma_utils.add_file('API文档.txt')
    print(ids)
    # retriever = chroma_utils.retriever()
    # print(retriever.invoke('创建用户的api信息'))
    # import chromadb
    # chroma = chromadb.PersistentClient(path=settings.VECTOR_STORE_DIR)
    # print(chroma.list_collections())
