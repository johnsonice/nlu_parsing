#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 15:46:04 2019

@author: huang
"""

import pandas as pd 
import numpy as np
import re 
import jieba
import copy
#%%

def read_sets(file_name,sheet_name):
    #pd.read_excel(file_name,sheet_name)
    set_df =  pd.read_excel(file_name,sheet_name).values.tolist()
    set_ids = [r[0] for r in set_df]
    # make sure their is no duplicates 
    assert len(set_ids) == len(set(set_ids)), "duplicate set ids, please check raw data"
    set_vals = [r[1:] for r in set_df]
    ## filter nan out of values 
    set_vals = [[i for i in r if not pd.isna(i)] for r in set_vals]
    set_dict_val = zip(set_ids,set_vals)
    set_dict = {i[0]:i[1] for i in set_dict_val}
    
    return set_dict

def read_pattern(file_name,sheet_name,id_column,pattern_column):
    df = pd.read_excel(file_name,sheet_name)
    id_pattern_pair = df[[id_column,pattern_column]].values.tolist()
    #print(id_pattern_pair[1])
    return id_pattern_pair

def process_pattern(p,set_dict,place_holder_dict=None):
    res = p.split('#')
    res = [detect_set(i.strip()) for i in res if i is not '']
    set_key_list = set_dict.keys()
    for r in res:
        if isinstance(r,list):
            for s in r:
                if s in set_key_list:
                    yield set_dict[s]
                else:
                    print('\nwaring, {} not in set list:{}\n'.format(s,p))
                    yield None
        else:
            if place_holder_dict:
                if r in place_holder_dict.keys():
                    yield place_holder_dict[r]
                else:
                    yield r
            else:
                yield r
            
def detect_set(p):
    setRegex = re.compile(r'<set>(.*?)</set>')
    res = setRegex.findall(p)
    if len(res)>0:
        return res
    else:
        return p 

def convert2record_list(id_pattern_pair,set_dict,place_holder_dict=None):
    res_dict = {'id':id_pattern_pair[0],
                'pattern':id_pattern_pair[1],
                'match_list': list(process_pattern(id_pattern_pair[1],set_dict,place_holder_dict))}
    return res_dict

def match_element(input_word,record):
    for wl in record['match_list']:
        if isinstance(wl,list):
            for w in wl:
                if input_word in str(w) and len(input_word)/len(str(w))>0.5:
                    return True
                else:
                    pass
        else:
            wl = str(wl)
            if input_word in wl and len(input_word)/len(wl)>0.5:
                return True
            else:
                pass
    return False 

def _match_pattern(input_list,record):
    record_copy = copy.copy(record)
    res = [match_element(i,record) for i in input_list]
    true_count = sum(res)
    input_length = len(res)
    record_length = len(record['match_list'])
    record_copy['input_score']=true_count/input_length
    record_copy['pattern_match_score']=true_count/record_length

#    res = {'input_score':true_count/input_length,
#          'pattern_match_score':true_count/record_length}
    return record_copy 
   
def match_patterns(input_list,record_list,input_thresh=0.5,pattern_thresh=0.5):
    #res_list = [(r,_match_pattern(input_list,r)) for r in record_list]
    res_list = [_match_pattern(input_list,r) for r in record_list]
    res_list = [r for r in res_list if r['pattern_match_score']>=pattern_thresh]
    res_list = [r for r in res_list if r['input_score']>=input_thresh]
    if len(res_list) == 0 :
        return None
    
    res_sorted = sorted(res_list, key = lambda x: ( x['input_score'],x['pattern_match_score']),reverse=True)
    
    return res_sorted

def check_dups(inpuyt_list):
    return None

#%%
if __name__ == "__main__":
    ## load data and pattern
    kb_path = "../../data/raw/knowledge_input.xlsx"
    set_dict = read_sets(kb_path,'sets')
    place_holder_dict = read_sets(kb_path,'place_holder')
    id_pattern_pairs = read_pattern(kb_path,'ask_pattern','Unnamed: 1','pattern')
    record_list = [convert2record_list(idpp,set_dict,place_holder_dict) for idpp in id_pattern_pairs]
    ## run one test 
    test = "你叫什么名字？"
    test = list(jieba.cut(test))
    res = match_patterns(test,record_list,0.6,0.6)
    res = match_patterns(test,res,0.6,0.7)
    
    print(res)

