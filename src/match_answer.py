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

#%%
kb_path = "../data/raw/knowledge_input.xlsx"
set_dict = read_sets(kb_path,'sets')
place_holder_dict = read_sets(kb_path,'place_holder')
id_pattern_pairs = read_pattern(kb_path,'ask_pattern','Unnamed: 1','pattern')
record_list = [convert2record_list(idpp,set_dict,place_holder_dict) for 
               idpp in id_pattern_pairs]
#%%

test_sentence = "我觉得你有什么厉害的？"
analyzer = han_analyzer()
processor = Processor(init_stop_words_path='./libs/init_stop_words.txt')
test_sentence = processor.remove_init_stop_words(test_sentence)
res = base_structure(test_sentence,analyzer)     
x = [i['lemma'] for i in res.loop_nodes(res.dep_tree,find_levels)]
ans = match_patterns(x,record_list,0.6,0.6)
ans = match_patterns(x,ans,0.6,0.7)
