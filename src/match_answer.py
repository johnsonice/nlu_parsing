#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 21:45:43 2019

@author: chengyu
"""

import sys 
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
#sys.path.insert(0,'./libs')
sys.path.insert(0,os.path.join(dir_path,'libs'))

from knowledge_bank_utils import read_sets,read_pattern,convert2record_list,match_patterns,get_intent_classes
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
from input_process_util import Processor
import pandas as pd
#%%
class NLU_match(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,kb_path,init_stop_words_path):
        self.set_dict = read_sets(kb_path,'sets')
        self.place_holder_dict = read_sets(kb_path,'place_holder')
        self.id_pattern_pairs = read_pattern(kb_path,'ask_pattern','intent_name','pattern')
        self.record_list = [convert2record_list(idpp,self.set_dict,self.place_holder_dict) for 
                            idpp in self.id_pattern_pairs]
        
        self.analyzer = han_analyzer()
        self.processor = Processor(init_stop_words_path=init_stop_words_path)
        self.base_structure = base_structure
        self.match_patterns = match_patterns
        self.get_intent_classes=get_intent_classes
        
        
    def get_dep_output_han(self,sentence):
        try:
            word_dict, word_objs = self.analyzer.dep_parse(sentence,False)  
            res = [(w['LEMMA'],w['POSTAG'],w['DEPREL'],w['HEAD_LEMMA']) for w in word_dict]
        except:
            print(sentence)
            res = None
        return res
    
    @staticmethod
    def find_levels(node):
        if node['level'] < 3:
            return True
        else:
            return False
    @staticmethod
    def find_levels2(node):
        if node['level'] < 5:
            return True
        else:
            return False
    
    def match(self,sentence,deep_match=False,match_intent=False):
        sentence = self.processor.check_and_remove_ini(sentence,self.analyzer,False)
        res = self.base_structure(sentence,self.analyzer)     
        eles = [i['lemma'] for i in res.loop_nodes(res.dep_tree,self.find_levels)]
        eles2 = [i['lemma'] for i in res.loop_nodes(res.dep_tree,self.find_levels2)]
        if len(eles)<1:
            print('log: your input sentence is empty')
            return None
        
        intent_classes=None
        if match_intent:
            intent_classes = self.get_intent_classes(sentence)
        
        ## start matching
        ans = self.match_patterns(eles,self.record_list,0.6,0.7,match_intent,intent_classes)
        if ans and deep_match and len(eles2)>len(eles):
            print('log: level > 2 info used for match')
            ans = self.match_patterns(eles2,ans,0.4,0.4)
            
        return ans

#%%
if __name__ == "__main__":
    kb_path = "../data/raw/knowledge_input.xlsx"
    init_stop_words_path = './libs/init_stop_words.txt'
    nlu = NLU_match(kb_path,init_stop_words_path)
    
    #%%
    test_sentence = "你觉得你有什么用？"
    ans = nlu.match(test_sentence,deep_match=True,match_intent=True)
    if ans:    
        print(ans[0])
    
    
    
    
    #%%
    
    
#    kb_path = "../data/raw/knowledge_input.xlsx"
#    test_file_path = "../data/raw/mdl_test_data.xlsx"
#    set_dict = read_sets(kb_path,'sets')
#    place_holder_dict = read_sets(kb_path,'place_holder')
#    id_pattern_pairs = read_pattern(kb_path,'ask_pattern','intent_name','pattern')
#    record_list = [convert2record_list(idpp,set_dict,place_holder_dict) for 
#                   idpp in id_pattern_pairs]
#    #%%
#    test_df = pd.read_excel(test_file_path,'test_corpus')
#    test_data = test_df['input'].tolist()
#    #%%
#    
#    analyzer = han_analyzer()
#    processor = Processor(init_stop_words_path='./libs/init_stop_words.txt')
#    
#    #%%
#    # run one test sentence 
#    test_sentence = "你觉得你有什么用？"
#    ans = match(test_sentence,processor,analyzer,record_list,deep_match=True)
#    
#    if ans:    
#        print(ans[0])
#        
#    #%%
#    res = []
#    res_deep = []
#    for t in test_data:
#        ans = match(t,processor,analyzer,record_list,deep_match=False)
#        ans_deep = match(t,processor,analyzer,record_list,deep_match=True)
#        if ans:
#            res.append(ans[0]['id'])
#        else:
#            res.append(ans)
#        
#        if ans_deep:
#            res_deep.append(ans_deep[0]['id'])
#        else:
#            res_deep.append(ans_deep)
#    #%%
#    df_data = zip(test_data,test_df['test_category'].tolist(),res,res_deep)
#    out_df = pd.DataFrame(df_data,columns=['input','test_category','res','res_deep'])
#    #%%
#    out_df.to_excel('../data/results/match_res.xlsx')