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
            ## test sentence 
        self.rule_map = {1: (self.rule_1,True),
                    2: (self.rule_2,True),
                    3: (self.rule_3,True),
                    4: (self.rule_4,False)}
        
        self.rule2name = {0: "其他",
                    1: "动词+主谓关系",
                    2: "动词+并列动词 没有主语",
                    3: "动词+名词",
                    4: "层数=2"}
        
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
    
    @staticmethod
    def rule_1(node):
        if node['level']>2 and node['node'].DEPREL == "主谓关系":
            return True
        else:
            return False
    
    @staticmethod
    def rule_2(node):
        if node['level']>1 and node['postag'][0].lower() == "v":
            return True
        else:
            return False
        
    @staticmethod
    def rule_3(node):
        if node['level']==2 and node['node'].DEPREL != "主谓关系" and node['postag'][0].lower() in ['n','r','a']:
            return True
        else:
            return False
        
    @staticmethod    
    def rule_4(node):
        if node['level']>2:
            return True
        else:
            return False
    
    def check_all_rules(self,sentance,analyzer):
        check = self._check_candidate(sentance)
        if check:
            res = base_structure(sentance,analyzer)
            for i in range(1,len(self.rule_map)+1):
                f_l = res.loop_nodes(res.dep_tree,self.rule_map[i][0])
                ## check if negation logic, it was set in rules maps
                if self.rule_map[i][1]:
                    if len(f_l) > 0:
                        return i
                    else:
                        pass
                else: ## this is negation logic 
                    if len(f_l) == 0:
                        return i
                    else:
                        pass
            return 0
        else:
            return 0 
        
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
    
    def check_and_remove_ini(self,input_sentance,analyzer,verbose=True):
        """
        function to process everything 
        """
        check = self.check_all_rules(input_sentance,analyzer)
        if verbose:
            print(check)
            print(self.rule2name[check])
        if check>0:
            res = base_structure(input_sentance,analyzer)
            out_sent = self.remove_init_stop_words(input_sentance,verbose)
            if verbose:
                res.print_dep_tree()
                ## check if rule satisfied 
                print(self.remove_init_stop_words(input_sentance))
            return out_sent
        else:
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
    #check = processor._check_candidate(test)
    check = processor.check_all_rules(test,analyzer)
    print(check)
    print(processor.rule2name[check])
    if check>0:
        res = base_structure(test,analyzer)
        res.print_dep_tree()
            ## check if rule satisfied 
        print(processor.remove_init_stop_words(test))
    
    
    # easy one function to process everything
    res = processor.check_and_remove_ini(test,verbose=False)    
    print(res)
