#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:11:39 2019

@author: chengyu
"""

#import pandas as pd
#import sys 
#sys.path.insert(0,'./libs')
#import stanfordnlp
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
#import numpy as np
import re
from input_process_util import Processor

#%%

class Long_sentence_processor(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,init_stop_words_path='init_stop_words.txt'):
        self.analyzer = han_analyzer()
        self.ini_processor = Processor(init_stop_words_path)
        
    @staticmethod
    def rule1(node):
        if node['level']>1 and node['postag'][0].lower() == "v":
            return True
        elif node['level']>1 and node['node'].DEPREL == "并列关系":
            return True
        else:
            return False
        
    @staticmethod
    def rule2(node):
        if node['postag'][0].lower() == "v":
            return True
        else:
            return False
        
    @staticmethod
    def check_candidates(sentence,verbose=True):
        ## simple normalization
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        
        ## check for comma and space
        if any(w in sentence for w in ['，',' ',',']):
            pass
        else:
            if verbose:
                print('no , or space found in the sentence')
            return False
        
        ## check sentence length 
        if len(sentence) <10:
            if verbose:
                print('sentence length < 10')
            return False
        
        ## chcek each compoment length
        eles = re.split(r'，| |,',sentence)
        if all(len(e)>4 for e in eles):
            pass
        else:
            if verbose:
                print('some components are <= 4 words')
            return False
        
        return True
    
    def check_dependency_rules(self,sentence,verbose=True):
        ## simple normalization
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        sentence = self.ini_processor.check_and_remove_ini(sentence,self.analyzer,verbose=False)
        
        ## check for complex dependency structure
        ob = base_structure(sentence,self.analyzer)
        if verbose:
            ob.print_dep_tree()
            
        r1_res = ob.loop_nodes(ob.dep_tree,self.rule1)
        if len(r1_res)==0:
            return False
        
        eles = re.split(r'，| |,',sentence)
        for e in eles:
            ob_e =  base_structure(e,self.analyzer)
            if verbose:
                ob_e.print_dep_tree()
            r2_res = ob_e.loop_nodes(ob_e.dep_tree,self.rule2)
            if len(r2_res) == 0:
                return False
            
        return True
    
    def check_and_split(self,sentence,verbose=False):
        ## first level check 
        if all([self.check_candidates(sentence,verbose=verbose),self.check_dependency_rules(sentence,verbose=verbose)]):
            #print('check passed')
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            eles = re.split(r'，| |,',sentence)
            return eles
        
        return sentence
        
    
#%%
if __name__ == '__main__':
    LP = Long_sentence_processor('./init_stop_words.txt')
    ts = ["可以和我说说你的工作原理是什么吗？",
          "想学点东西，你觉得学什么好",
          "你会通过什么方式来赚钱",
          "对于XX的前景，你怎么看",
          "能告诉我你的信息在哪里得来的？",
          "我认为你是一个没有什么价值的机器人"]
    for s in ts:
        print(LP.check_and_split(s))

    



