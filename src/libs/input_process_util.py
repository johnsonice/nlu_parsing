#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 20:57:30 2019

@author: huang
"""
import re
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure

class Processor(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,init_stop_words_path='init_stop_words.txt'):
        self.init_stop_words = self.read_text(init_stop_words_path)
        
    @staticmethod
    def read_text(file_path):
        with open(file_path, "r") as f:
            input_list = f.readlines()
            input_list = [i.strip('\n').strip() for i in input_list]
        return input_list
    
    def _check_candidate(self,input_sentance,verbose=False):
        stop_words = self.init_stop_words
        if len(input_sentance)==0:
            if verbose:
                print('warning: input sentence is empty')
            return input_sentance
        
        for sw in stop_words:
            res = re.search(sw,input_sentance)
            if res is None:
                continue
            elif res.start() == 0:
                if verbose:
                    print('Initial stop words detected: [{}] {}'.format(sw,input_sentance))
                return True
            else:
                continue
            
        return False
    
    def remove_init_stop_words(self,input_sentance,verbose=True):
        
        stop_words = self.init_stop_words
        
        if len(input_sentance)==0:
            if verbose:
                print('warning: input sentence is empty')
            return input_sentance
        
        for sw in stop_words:
            res = re.search(sw,input_sentance)
            if res is None:
                continue
            elif res.start() == 0:
                if verbose:
                    print("[{}] removed from: {}.".format(sw,input_sentance))
                return input_sentance.replace(sw,'',1)
            else:
                continue
        
        return input_sentance
    
#    def check_filter_rules(self,input_sentance):
#        stop_words = self.init_stop_words
        

#%%
if __name__=="__main__":
    processor = Processor(init_stop_words_path='init_stop_words.txt')
    analyzer = han_analyzer()
    
    ## test sentence 
    test = "你觉得旅游必去的地方有哪些？"
    ## check if it is start with stop words
    check = processor._check_candidate(test)
    print(check)
    if check:
        res = base_structure(test,analyzer)
        res.print_dep_tree()
        
    ## define filter rule 
    def filter_f(node):
        if node['level']>2 and node['node'].DEPREL == "主谓关系":
            return True
        else:
            return False
        
    ## check if rule satisfied 
    f_l = res.loop_nodes(res.dep_tree,filter_f)
    if len(f_l)>0:
        print(processor.remove_init_stop_words(test))
        for f in f_l:
            print(f['lemma'],f['node'].DEPREL)