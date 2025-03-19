#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:quincy qiang
@license: Apache Licence
@file: RagApplication.py
@time: 2024/05/20
@contact: yanqiangmiffy@gamil.com
"""
import os

from trustrag.modules.citation.match_citation import MatchCitation
from trustrag.modules.document.common_parser import CommonParser
from trustrag.modules.generator.llm import GLM4Chat
from trustrag.modules.reranker.bge_reranker import BgeReranker
from trustrag.modules.retrieval.dense_retriever import DenseRetriever
from trustrag.modules.document.chunk import TextChunker
from trustrag.modules.retrieval.embedding import FlagModelEmbedding
class ApplicationConfig():
    def __init__(self):
        self.retriever_config = None
        self.rerank_config = None


class RagApplication():
    def __init__(self, config):
        self.config = config
        self.parser = CommonParser()
        self.embedding_generator = FlagModelEmbedding(self.config.retriever_config.model_name_or_path)
        self.retriever = DenseRetriever(self.config.retriever_config,self.embedding_generator)
        self.reranker = BgeReranker(self.config.rerank_config)
        self.llm = GLM4Chat(self.config.llm_model_path)
        self.mc = MatchCitation()
        self.tc=TextChunker()
    def init_vector_store(self):
        """

        """
        print("init_vector_store ... ")
        all_paragraphs = []
        all_chunks = []
        for filename in os.listdir(self.config.docs_path):
            file_path = os.path.join(self.config.docs_path, filename)
            try:
                paragraphs=self.parser.parse(file_path)
                all_paragraphs.append(paragraphs)
            except:
                pass
        print("chunking for paragraphs")
        for paragraphs in all_paragraphs:
            chunks=self.tc.get_chunks(paragraphs, 256)
            all_chunks.extend(chunks)
        self.retriever.build_from_texts(all_chunks)
        print("init_vector_store done! ")
        self.retriever.save_index(self.config.retriever_config.index_path)

    def load_vector_store(self):
        self.retriever.load_index(self.config.retriever_config.index_path)

    def add_document(self, file_path):
        chunks = self.parser.parse(file_path)
        for chunk in chunks:
            self.retriever.add_text(chunk)
        print("add_document done!")

    def chat(self, question: str = '', top_k: int = 5):
        contents = self.retriever.retrieve(query=question, top_k=top_k)
        contents = self.reranker.rerank(query=question, documents=[content['text'] for content in contents])
        content = '\n'.join([content['text'] for content in contents])
        print(contents)
        result, history = self.llm.chat(question, [], content)
        # result = self.mc.ground_response(
        #     response=response,
        #     evidences=[content['text'] for content in contents],
        #     selected_idx=[idx for idx in range(len(contents))],
        #     markdown=True
        # )
        return result, history, contents
