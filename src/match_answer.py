#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 21:45:43 2019

@author: chengyu
"""

import sys 
sys.path.insert(0,'./libs')

from knowledge_bank_utils import read_sets,read_pattern,convert2record_list,match_patterns
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
from input_process_util import Processor
import pandas as pd
#%%

def get_dep_output_han(sentence,han_analyser):
    try:
        word_dict, word_objs = han_analyser.dep_parse(sentence,False)  
        res = [(w['LEMMA'],w['POSTAG'],w['DEPREL'],w['HEAD_LEMMA']) for w in word_dict]
    except:
        print(sentence)
        res = None
    return res


def find_levels(node):
    if node['level'] < 3:
        return True
    else:
        return False
    
def find_levels2(node):
    if node['level'] < 5:
        return True
    else:
        return False

def match(sentence,processor,analyzer,record_list,deep_match=False):
    sentence = processor.check_and_remove_ini(sentence,analyzer,False)
    res = base_structure(sentence,analyzer)     
    eles = [i['lemma'] for i in res.loop_nodes(res.dep_tree,find_levels)]
    eles2 = [i['lemma'] for i in res.loop_nodes(res.dep_tree,find_levels2)]
    
    ans = match_patterns(eles,record_list,0.6,0.7)
    if ans and deep_match:
        print('level > 2 info used for match')
        ans = match_patterns(eles2,ans,0.4,0.4)
    return ans

#%%
if __name__ == "__main__":
    kb_path = "../data/raw/knowledge_input.xlsx"
    test_file_path = "../data/raw/mdl_test_data.xlsx"
    set_dict = read_sets(kb_path,'sets')
    place_holder_dict = read_sets(kb_path,'place_holder')
    id_pattern_pairs = read_pattern(kb_path,'ask_pattern','Unnamed: 1','pattern')
    record_list = [convert2record_list(idpp,set_dict,place_holder_dict) for 
                   idpp in id_pattern_pairs]
    #%%
    test_df = pd.read_excel(test_file_path,'test_corpus')
    test_data = test_df['input'].tolist()
    #%%
    
    analyzer = han_analyzer()
    processor = Processor(init_stop_words_path='./libs/init_stop_words.txt')
    
    #%%
    # run one test sentence 
    test_sentence = "你觉得你有什么用？"
    ans = match(test_sentence,processor,analyzer,record_list,deep_match=False)
    
    if ans:    
        print(ans[0])
        
    #%%
    res = []
    res_deep = []
    for t in test_data:
        ans = match(t,processor,analyzer,record_list,deep_match=False)
        ans_deep = match(t,processor,analyzer,record_list,deep_match=True)
        if ans:
            res.append(ans[0]['id'])
        else:
            res.append(ans)
        
        if ans_deep:
            res_deep.append(ans_deep[0]['id'])
        else:
            res_deep.append(ans_deep)
    #%%
    df_data = zip(test_data,test_df['test_category'].tolist(),res,res_deep)
    out_df = pd.DataFrame(df_data,columns=['input','test_category','res','res_deep'])
    #%%
    out_df.to_excel('../data/results/match_res.xlsx')