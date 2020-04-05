#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 10:48:43 2018

@author: chengyu
"""
## online training word embedding 

#from gensim.corpora.wikicorpus import WikiCorpus
from gensim.models.word2vec import Word2Vec#, LineSentence
from copy import deepcopy
#from multiprocessing import cpu_count
import os
import pandas as pd
import jieba
#%%


def w2v_train(pre_trained_model_path,sentances_tokens,workers=4,window=None,epochs=10,save_path=None):
    """"
    inputs:
        pretrained model path
        list of tokenized sentences
    """
    ## load pretrained model
    model_pretrain = Word2Vec.load(pre_trained_model_path)
    
    ## build vocabulary
    new_model = deepcopy(model_pretrain)
    new_model.build_vocab(sentances_tokens, update=True)
    
    ## set premeters 
    if window:   
        new_model.window=window
    if workers:
        new_model.workers=workers
    
    ## train model 
    new_model.train(sentances_tokens, 
                    total_examples=model_pretrain.corpus_count, 
                    epochs=epochs)
    
    ## save model 
    if save_path:
        new_model.save(save_path)
    
    return new_model


if __name__ == "__main__":
    ## data path
    data_folder = '/home/chengyu/Dev/All_chatbot_models/nlu_parsing/data/w2v'
    data_path = os.path.join(data_folder,'training_data/w2v_train_merge.csv')
    w2v_pretain_model = os.path.join(data_folder,'pre_trained_embedding/w2v', 'zh.bin')

    ## load all training data
    sentances = pd.read_csv(data_path,header=None)[0].values.tolist()
    ## tokenize sentances 
    sentances_tokens = [list(jieba.cut(s)) for s in sentances]
    
    ## train and save model 
    model_pretrain = Word2Vec.load(w2v_pretain_model)
    
    new_model = w2v_train(pre_trained_model_path=w2v_pretain_model,
                          sentances_tokens=sentances_tokens,
                          workers=8,
                          window=5,
                          epochs=20,
                          save_path=os.path.join(data_folder,'pre_trained_embedding/w2v/updated.w2v'))
    

    ## Evaluate
    #incrrase in vocabulary
    for m in [model_pretrain, new_model]:
        print('The vocabulary size of the', m, 'is', len(m.wv.vocab))
    
    freq_wd_list = ['买', '机器人', '功能', '觉得', '特性', '介绍', '什么']
    for m in freq_wd_list:
        print('The similar words of ', m, 'in the old model is \n', model_pretrain.wv.similar_by_word(m))
        print('\n')
        print('The similar words of ', m, 'in the new model is \n', new_model.wv.similar_by_word(m))
        print('\n')
        print('========================================================')