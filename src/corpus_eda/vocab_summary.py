#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 23:00:50 2019

@author: chengyu
"""
import os
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
key_tags = ['n','x','v','a','q','d','r','eng','m']

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
                       key_tags=['n','v','a','q','d','r','eng','m'],
                       total_count=None):
    """
    tagged_sentences : a list of sentences, all tokenized and tagged, all elements are (w.pos)
    key_tags : tags we want to look at
    """
    res = {}
    for kt in key_tags:
        kt_C = Counter([p[0] for li in tagged_sentences for p in li if p[1]==kt ])
        df_C =  pd.DataFrame(kt_C.most_common(),columns=[kt,'count'])
        if isinstance(total_count,int):
            df_C['prob'] = df_C['count']/total_count 
        
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
        corpus_cooccure = [l for l in corpus_cooccure if len(l)>num-1]
    return corpus_cooccure
    

def multi_key_summary(tagged_sentences,
                        key_tags=['n','v','a','q','d','r','eng','m'],
                        num=2,
                        order=False,
                        total_count=None):
    """
    total_count; overall denominator of your corpus, if you want probability 
    """
    corpus_cooccure = _build_cooccure_sets(tagged_sentences,key_tags,num,order=order)
    kt_C = Counter(corpus_cooccure)
    df_C =  pd.DataFrame(kt_C.most_common(),columns=['co-occure','count'])
    if isinstance(total_count,int):
        df_C['prob'] = df_C['count']/total_count 
        
    return df_C

def _convert_to_pos_pattern(tagged_sentence):
    pos_pattern = "-".join([p[1] for p in tagged_sentence])
    return pos_pattern

def get_common_pos_pattern(tagged_sentences,topn=None):
    """
    Get common pos pattern and return df 
    """
    
    pos_patterns = [_convert_to_pos_pattern(t) for t in tagged_sentences]
    C = Counter(pos_patterns)
    df_C =  pd.DataFrame(C.most_common(),columns=['pos_pattern','count'])
    if isinstance(topn,int):
        df_C = df_C.head(topn)
    
    return df_C

def get_by_pos_pattern(pos_pattern,tagged_sentences):
    """
    pos_pattern: e.g 'v-v-n'
    tagged_sentences: pos tagged sentences 
    """
    data = [p for p in tagged_sentences if _convert_to_pos_pattern(p) == pos_pattern]
    C = Counter(data)
    df_C =  pd.DataFrame(C.most_common(),columns=[pos_pattern,'count'])
    return df_C

def export_to_excel(file_name,res_dict):
    with pd.ExcelWriter(file_name) as writer:  # doctest: +SKIP
        for k,v in res_dict.items():
            v.to_excel(writer, sheet_name=k)

#%%
if __name__ =="__main__":
    EXPORT = True
    
    
    ## load and clean data 
    corpus_path = "../../data/raw/corpus/victor.xlsx"
    corpus_res_folder = '../../data/results/corpus'
    df = pd.read_excel(corpus_path)
    corpus = df['Question'].values.tolist()
    corpus_clean = [l.lower().strip().replace(" ","") for l in corpus]  ## merge all english words into one
    
    ## get pos tagged data
    corpus_pos = [pos_tag(l) for l in corpus_clean]
    
    # single word analysis
    LEN = len(corpus_pos)
    single_res = single_key_summary(corpus_pos,total_count=LEN)
    print(single_res['n'].head(10))
    if EXPORT:
        f_name = os.path.join(corpus_res_folder,'1_token.xlsx')
        export_to_excel(f_name,single_res)

#%%
    # multi words analysis 
    k_tags=['n','v','a','q','d','eng','m']  ## 删掉代词 r 
    for i in range(2,5):
        res = {}
        c = multi_key_summary(corpus_pos,key_tags=k_tags,num=i,order=True,total_count=LEN)
        print(c.head(10))   ## there is a bug . why 
        res['overall_rank'] = c
        #%%
        # analysis pos patterns 
        tagged_pos_data = c['co-occure'].values.tolist()
        pos_df = get_common_pos_pattern(tagged_pos_data)
        print(pos_df.head(20))
        res['pos_pattern_rank'] = pos_df
        #%%
        top_pos_patterns = pos_df.head(10)['pos_pattern'].values.tolist()
        for one_pos_pattern in top_pos_patterns:
            filtered_corpus_pos = _build_cooccure_sets(corpus_pos,num=i,order=True)
            pos_pattern_df = get_by_pos_pattern(one_pos_pattern,filtered_corpus_pos)
            print(pos_pattern_df.head(10))
            res[one_pos_pattern] = pos_pattern_df
            
        ## export to excel 
        f_name = os.path.join(corpus_res_folder,'{}_toekn.xlsx'.format(i))
        export_to_excel(f_name,res)
        
        
        
        