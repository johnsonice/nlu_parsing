#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 10:48:43 2018

@author: chengyu
"""
## online training word embedding 

#from gensim.corpora.wikicorpus import WikiCorpus
from gensim.models.word2vec import Word2Vec, LineSentence
from pprint import pprint
from copy import deepcopy
#from multiprocessing import cpu_count
#from smart_open import smart_open
import os
import pickle
import re
import string
import pandas as pd
import jieba

#%%
def clean(line,punc_list):
    l = line.replace('_',' ')
    l = re.sub(r"[" + re.escape(punc_list) + r"]",'',l)
    l = l.strip()
    
    l = re.sub('[0-9a-zA-Z]+', '', l)
    if len(l)<4:
        return False
    
    return True

if __name__ == "__main__":
    ## load all training data
    dat_user = pd.read_csv("../data/dat_real0812.csv")
    dat_simulate = pd.read_csv("../data/df_real_morethan5_sample0812.csv")
    sentances = dat_user['input'].astype(str)
    sentances.append(dat_user['output'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['input'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['output'].astype(str),ignore_index=True)
    sentances.dropna(inplace=True)
    
    ## remove noisy and short sentances
    punc_list = "。，？‘；】【「」、|～！·"+string.punctuation
    print('length of org sentances: {}'.format(len(sentances)))
    sentances_clean = [s for s in sentances if clean(s,punc_list)]
    del sentances
    print('length of cleaned sentances: {}'.format(len(sentances_clean)))
    
    ## tokenize sentances 
    sentances_tokens = [list(jieba.cut(s)) for s in sentances_clean]
    
    ## load pretrained model 
    #%%
    data_path = os.path.join('../pre_trained_embedding/w2v', 'zh.bin')
    model_pretrain = Word2Vec.load(data_path)
    
    new_model = deepcopy(model_pretrain)
    new_model.build_vocab(sentances_tokens, update=True)
    new_model.train(sentances_tokens, 
                    total_examples=model_pretrain.corpus_count, 
                    epochs=50)
    
    new_model.save('../pre_trained_embedding/w2v/updated.w2v')
    
    #%% incrrase in vocabulary
    for m in ['model_pretrain', 'new_model']:
        print('The vocabulary size of the', m, 'is', len(eval(m).wv.vocab))
    
    ## Evaluate
    old_vocab = set(model_pretrain.wv.vocab.keys())
    new_vocab = set(new_model.wv.vocab.keys())
    vocab_added = new_vocab - old_vocab
    print(vocab_added)
    
    freq_wd_list = ['买', '机器人', '功能', '觉得', '特性', '双子座', '什么']
    for m in freq_wd_list:
        print('The similar words of ', m, 'in the old model is \n', model_pretrain.wv.similar_by_word(m))
        print('\n')
        print('The similar words of ', m, 'in the new model is \n', new_model.wv.similar_by_word(m))
        print('\n')
        print('========================================================')