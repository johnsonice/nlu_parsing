#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 21:00:54 2020

@author: chengyu
"""

## gensim version 3.8 

from gensim.models.word2vec import Word2Vec#, LineSentence
import os

class WV(object):
    """"
    simple w2v inference model 
    """
    def __init__(self,model_path):
        '''
        input: trained model path
        '''
        self.model = Word2Vec.load(model_path)
    
    def get_sim(self,key,topn=10):
        """"
        key = key words you want to find sim words for 
        topn = top n most similar words 
        """
        return self.model.wv.most_similar(key,topn=topn)
    
    
    
if __name__ == "__main__":
    ## data path
    data_folder = '/home/chengyu/Dev/All_chatbot_models/nlu_parsing/data/w2v'
    model_path = os.path.join(data_folder,'pre_trained_embedding/w2v', 'updated.w2v')
    
    ## load model 
    wv_model = WV(model_path)
    
    ## inference 
    print(wv_model.get_sim('功能',topn=10))