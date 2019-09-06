#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 23:00:50 2019

@author: chengyu
"""

import pandas as pd 
import numpy as np
import jieba 
import copy
import jieba.posseg as pseg
from collections import Counter
#import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from scipy.sparse import csr_matrix
from itertools import combinations
dir_dict = "../../data/processed/my_dict.txt"
jieba.load_userdict(dir_dict)
#%%
key_tags = ['n','v','a','q','d','r','eng','m']

def group_pos(pos):
    groups = {'n':['ns', 'n', 'nt', 'nr', 'nrt', 'nz'],
              'v':['v', 'vg', 'vd','vn'],
              'a':['ag', 'a', 'ad','an'],
              'd':['df']
              }
    
    for k,v in groups.items():
        if pos in v:
            return k
    
    return pos

def pos_tag(sent):
    res = [ (s,group_pos(pos)) for s,pos in pseg.cut(sent)]
    return res

def get_tag_word(l,tag):
    res = [i[0] for i in l if str.startswith(i[1],tag)]
    res = ' '.join(res)
    return res

def single_key_summary(tagged_sentences,
                       key_tags=['n','v','a','q','d','r','eng','m']):
    """
    tagged_sentences : a list of sentences, all tokenized and tagged, all elements are (w.pos)
    key_tags : tags we want to look at
    """
    res = {}
    for kt in key_tags:
        kt_C = Counter([p[0] for li in corpus_pos for p in li if p[1]==kt ])
        df_C =  pd.DataFrame(kt_C.most_common(),columns=[kt,'count'])
        res[kt] = df_C
    
    return res

def _filter_corpus(tagged_sentences,
                      key_tags=['n','v','a','q','d','r','eng','m'],
                      min_n = 2):
    """
    tagged_sentences : a list of sentences, all tokenized and tagged, all elements are (w.pos)
    key_tags : tags we want to look at
    """
    
    filtered_tagged_sentences = [[p for p in s if p[1] in key_tags] for s in tagged_sentences]
    filtered_tagged_sentences = [s for s in filtered_tagged_sentences if len(s)>min_n-1]
    return filtered_tagged_sentences

def _flatten(l):
    for el in l:
        if isinstance(el, list) and not isinstance(el, (str, bytes)):
            yield from _flatten(el)
        else:
            yield el
            
def _build_cooccure_sets(tagged_sentences,
                        key_tags=['n','v','a','q','d','r','eng','m'],
                        num=2,
                        order=False):
    """
    tagged_sentences : a list of sentences, all tokenized and tagged, all elements are (w.pos)
    key_tags : tags we want to look at
    """
    corpus = _filter_corpus(tagged_sentences,key_tags,num)
    corpus_cooccure = [list(combinations(l,num)) for l in corpus]
    corpus_cooccure = list(_flatten(corpus_cooccure))
    if order:
        pass
    else:
        corpus_cooccure = [set(l) for l in corpus_cooccure]  ## we don't care about sequence order
        corpus_cooccure = [tuple(l) for l in corpus_cooccure] ## change back to tuple, for Counter to work
    return corpus_cooccure
    

def multi_key_summary(tagged_sentences,
                        key_tags=['n','v','a','q','d','r','eng','m'],
                        num=2,
                        order=False):

    corpus_cooccure = _build_cooccure_sets(tagged_sentences,key_tags,num)
    kt_C = Counter(corpus_cooccure)
    df_C =  pd.DataFrame(kt_C.most_common(),columns=['co-occure','count'])
    
    return df_C
#%%
if __name__ =="__main__":
    corpus_path = "../../data/raw/corpus/victor.xlsx"
    df = pd.read_excel(corpus_path)
    corpus = df['Question'].values.tolist()
    corpus_clean = [l.lower().strip() for l in corpus]
    corpus_pos = [pos_tag(l) for l in corpus_clean]
    single_res = single_key_summary(corpus_pos)
#%%
    c = multi_key_summary(corpus_pos,num=4,order=False)
    c.head(20)   ## there is a bug . why 