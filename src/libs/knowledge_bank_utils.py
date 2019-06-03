#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 15:46:04 2019

@author: huang
"""

import pandas as pd 
import numpy as np
import re 
from request_util import get_intent
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

def read_pattern(file_name,sheet_name,id_column,pattern_column,intent_c1='intent_class_1', intent_c2='intent_class_2'):
    df = pd.read_excel(file_name,sheet_name)
    #id_pattern_pair = df[[id_column,pattern_column]].values.tolist()
    id_pattern_pair = df[[id_column,pattern_column,intent_c1,intent_c2]].values.tolist()
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
                'intent_class_1':id_pattern_pair[2],
                'intent_class_2':id_pattern_pair[3],
                'match_list': list(process_pattern(id_pattern_pair[1],set_dict,place_holder_dict))}
    return res_dict

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def match_element_with_order(input_word,record):
    for idx,wl in enumerate(record['match_list']):
        if isinstance(wl,list):
            for w in wl:
                if input_word in str(w) and len(input_word)/len(str(w))>0.5:
                    return idx
                else:
                    pass
        else:
            wl = str(wl)
            if input_word in wl and len(input_word)/len(wl)>0.5:
                return idx
            else:
                pass
    return False 

def _match_pattern(input_list,record):
    record_copy = copy.copy(record)
    res = [match_element_with_order(i,record_copy) for i in input_list]
    res = [r for r in res if not r is False]
    true_count_input = len(res)
    input_length = len(input_list)
    true_count_record = len(set(res))
    record_length = len(record_copy['match_list'])
    record_copy['input_score']=true_count_input/input_length
    pm_score = true_count_record/record_length
    if pm_score >= 1 :
        res_set = unique(res)
        ords = all(i < j for i, j in zip(res_set, res[1:])) 
        if ords:
            record_copy['pattern_match_score']=pm_score + 1 
        else:
            record_copy['pattern_match_score']=pm_score
    else:
        record_copy['pattern_match_score']=pm_score
    
#    res = {'input_score':true_count/input_length,
#          'pattern_match_score':true_count/record_length}
    return record_copy 


def match_patterns(input_list,record_list,input_thresh=0.5,pattern_thresh=0.5,match_intent=False,intent_classes=None):
    #res_list = [(r,_match_pattern(input_list,r)) for r in record_list]
    if match_intent and intent_classes:
        print('log: apply intent filter')
        res_list  = [r for r in record_list if (intent_classes['lv1'] in r['intent_class_1'] and intent_classes['lv2'] in r['intent_class_2'])]
        #print(len(res_list),len(record_list))
    else:
        res_list = record_list
        
    res_list = [_match_pattern(input_list,r) for r in res_list]
    res_list = [r for r in res_list if r['pattern_match_score']>=pattern_thresh]
    res_list = [r for r in res_list if r['input_score']>=input_thresh]
    if len(res_list) == 0 :
        return None
    
    res_sorted = sorted(res_list, key = lambda x: ( x['input_score'],x['pattern_match_score']),reverse=True)
    
    return res_sorted

def get_intent_classes(text):
    res = {}
    try:
        intent = get_intent(text)
        res['lv1'] = intent['text']['lv1']['label']
        res['lv2'] = intent['text']['lv2']['label']
        res['lv3'] = intent['text']['lv3']['label']
    except Exception as e:
        print(e)
        return None
    
    return res

def check_dups(input_list):
    return None

#%%
if __name__ == "__main__":
    ## load data and pattern
    kb_path = "../../data/raw/knowledge_input.xlsx"
    set_dict = read_sets(kb_path,'sets')
    place_holder_dict = read_sets(kb_path,'place_holder')
    id_pattern_pairs = read_pattern(kb_path,'ask_pattern','intent_name','pattern')
    record_list = [convert2record_list(idpp,set_dict,place_holder_dict) for idpp in id_pattern_pairs]
    #%%
    ## run one test 
    test = "你叫什么名字？"
    intent = get_intent_classes(test)
    test = list(jieba.cut(test))
    res = match_patterns(test,record_list,0.6,0.6,match_intent=False,intent_classes=intent)
    #%%
    res = match_patterns(test,res,0.6,0.7)
    
    print(res)

