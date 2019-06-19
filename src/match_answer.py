#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 21:45:43 2019

@author: chengyu
"""

import sys 
import os 
try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
except:
    dir_path = '.'
#sys.path.insert(0,'./libs')
sys.path.insert(0,os.path.join(dir_path,'libs'))

from knowledge_bank_utils import read_sets,read_pattern,convert2record_list,match_patterns,get_intent_classes
from chatbot_keywords_utils import read_keywords
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
from input_process_util import Processor
from long_sentence_process import Long_sentence_processor
#import pandas as pd

import logging
logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.DEBUG)

#%%
class RB2(object):
    """
    rule base 2 functionalities 
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,kb_path,init_stop_words_path,keywords_path):
        self.set_dict = read_sets(kb_path,'sets')
        self.place_holder_dict = read_sets(kb_path,'place_holder')
        self.id_pattern_pairs = read_pattern(kb_path,'ask_pattern','intent_id','pattern')
        self.record_list = [convert2record_list(idpp,self.set_dict,self.place_holder_dict) for 
                            idpp in self.id_pattern_pairs]
        
        self.keyword_dict = read_keywords(keywords_path)
        self.analyzer = han_analyzer()
        self.processor = Processor(init_stop_words_path=init_stop_words_path)
        self.base_structure = base_structure
        self.match_patterns = match_patterns
        self.get_intent_classes=get_intent_classes
        self.long_sentence_processor = Long_sentence_processor(init_stop_words_path)
        
        
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
    
    @staticmethod
    def filter_and_rank(res_obj,find_level_func):
        #eles = [i['lemma'] for i in res_obj.loop_nodes(res_obj.dep_tree,find_level_func)]
        eles = [(i['id'],i['lemma']) for i in res_obj.loop_nodes(res_obj.dep_tree,find_level_func)]
        eles = sorted(eles,key = lambda x:x[0])
        eles = [x[1] for x in eles]
        return eles
    
    def match_one(self,sentence,deep_match=False,match_intent=False,topn=5):
        sentence = self.processor.check_and_remove_ini(sentence,self.analyzer,False)
        res = self.base_structure(sentence,self.analyzer)     
        #eles = [i['lemma'] for i in res.loop_nodes(res.dep_tree,self.find_levels)]
        eles = self.filter_and_rank(res,self.find_levels)
        #print(eles)
        #eles2 = [i['lemma'] for i in res.loop_nodes(res.dep_tree,self.find_levels2)]
        eles2 = self.filter_and_rank(res,self.find_levels2)
        #print(eles2)
        if len(eles)<1:
            print('log: your input sentence is empty')
            return None
        
        intent_classes=None
        if match_intent:
            intent_classes = self.get_intent_classes(sentence)
        
        ## start matching
        ans = self.match_patterns(eles,self.record_list,self.keyword_dict,0.4,0.7,match_intent,intent_classes)
        if ans and deep_match and len(eles2)>len(eles):
            print('log: level > 2 info used for match')
            ans = self.match_patterns(eles2,ans,self.keyword_dict,0.3,0.6)
            
        return ans[:topn]
    
    def match(self,sentence,deep_match=False,match_intent=False,topn=5,check_long_sentence=True):
        
        if check_long_sentence:
            processed_inputs = self.long_sentence_processor.check_amd_split(sentence)
            logging.info(processed_inputs)
            if isinstance(processed_inputs, (list,)):
                res = {
                        'answer1':self.match_one(processed_inputs[0],
                                                deep_match=deep_match,
                                                match_intent=match_intent,
                                                topn=topn),
                       'asnwer2':self.match_one(processed_inputs[1],
                                                deep_match=deep_match,
                                                match_intent=match_intent,
                                                topn=topn)
                       }
            else:
                res = {'answer1':self.match_one(processed_inputs[0],
                                            deep_match=deep_match,
                                            match_intent=match_intent,
                                            topn=topn),
                        'asnwer2':None}
        else:
            res = {'answer1':self.match_one(processed_inputs[0],
                                            deep_match=deep_match,
                                            match_intent=match_intent,
                                            topn=topn),
                   'asnwer2':None}
        
        return res
    
    def evaluate_pattern(self,sentence,input_pattern,deep_match=False,match_intent=False):
        try:
            record = convert2record_list(['input_id',input_pattern,'NA','NA'],self.set_dict,self.place_holder_dict)
            sentence = self.processor.check_and_remove_ini(sentence,self.analyzer,False)
            res = self.base_structure(sentence,self.analyzer)
            #eles = self.filter_and_rank(res,self.find_levels)
            eles2 = self.filter_and_rank(res,self.find_levels2)
            ans = self.match_patterns(eles2,[record],self.keyword_dict,0.0,0.0,match_intent,None)
        
        except Exception as e:
            #logging.warning('Problem with input')
            logging.warning(e)
            return None
        
        return ans[0]

#%%
if __name__ == "__main__":
    #kb_path = "../data/raw/knowledge_input.xlsx"
    kb_path = "../data/raw/victor_knowledge_input.xlsx"
    init_stop_words_path = './libs/init_stop_words.txt'
    chatbot_keywords_path = "../data/raw/chatbot_keywords.csv"
    nlu = RB2(kb_path,init_stop_words_path,chatbot_keywords_path)
    #%%
    # run one example 
    test_sentence = "你觉得你能教我学乐器吗？"
    test_sentence= "这句话应该分成两句，你能帮我做些什么事情呢？"
    #%%
    #test_sentence= "你能说说伦敦的房地投资机会怎么样"
    ans = nlu.match(test_sentence,deep_match=True,match_intent=False,topn=1,check_long_sentence=True)
    print(ans)
    #%%
    input_pattern = '<set>Victor</set>#<set>可以</set>#<set>描述</set>#'
    #input_pattern=None
    res = nlu.evaluate_pattern(test_sentence,input_pattern)
    print(res)
    #%%

#    res = nlu.base_structure(test_sentence,nlu.analyzer)
#    res.print_dep_tree()
#    ## remove initial 
#    test_sentence = nlu.processor.check_and_remove_ini(test_sentence,nlu.analyzer,False)
#    res = nlu.base_structure(test_sentence,nlu.analyzer)
#    res.print_dep_tree()

##%%
#    #eles = [i['lemma'] for i in res.loop_nodes(res.dep_tree,nlu.find_levels)]
#    eles = nlu.filter_and_rank(res,nlu.find_levels2)
#    print('level 2 nodes: {}'.format(eles))
#    
    
    
#    
#    #%%
#    run_all= False 
#    if run_all:
#        def get_top_answer(ask,nlu=nlu):
#            ans = nlu.match(ask,deep_match=True,match_intent=False)
#            if ans:
#                return ans[0]['id']
#            else:
#                return None
#            
#        test_file_path = '../data/raw/test_data.csv'
#        data = pd.read_csv(test_file_path)
#        data['res'] = data['input'].apply(get_top_answer)
#        data.to_csv('../data/results/nlu_test_res.csv')