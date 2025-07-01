#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


class Settings:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_PATH = os.path.join(BASE_PATH, "logs")
    VECTOR_STORE_DIR = os.path.join(BASE_PATH, "chroma_db")


settings = Settings()
