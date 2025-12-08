import time
import sys
import os
from dataclasses import dataclass
from langchain_community.vectorstores import Chroma, FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

from src.logger import logging
from src.exception import CustomException

@dataclass
class RetrievalConfig:
    chroma_db_path=os.path.join('data','chroma_db')
    faiss_db_path=os.path.join('data','faiss_index')

class Retrieval:
    def __init__(self):
        self.retrival_config=RetrievalConfig()
        self.embedding_model=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

        logging.info('loading on dist dbs')
        try:
            self.faiss_db=FAISS.load_local(
                self.retrieval_config.faiss_db_path, 
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            self.chroma_db=Chroma(
                persist_directory=self.retrieval_config.chroma_db_path, 
                embedding_function=self.embedding_model
            )
            logging.info('dbs loaded!')
        except Exception as e:
            logging.info('could not load dbs run the ingestion first')
            self.faiss_db=None
            self.chroma_db=None
    
    def initiate_retrival(self,cyborg_db,query):
        metrics={}

        try:
            if self.chroma_db:
                logging.info('retriving from chroma')
                st_time=time.time()
                _=self.chroma_db.similarity_search(query,1)
                metrics['chroma']=time.time()-st_time
            
            if self.faiss_db:
                logging.info('retriving from faiss')
                st_time=time.time()
                _=self.faiss_db.similarity_search(query,1)
                metrics['faiss_db']=time.time()-st_time

            logging.info('retriving from cyborg_db')
            st_time=time.time()
            result=cyborg_db.similarity_search(query)
            metrics['cyborg_db']=time.time()-st_time

            return metrics,result

        except Exception as e:
            raise CustomException(e,sys)
