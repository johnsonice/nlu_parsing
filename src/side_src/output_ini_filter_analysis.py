#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 21:25:13 2019

@author: chengyu
"""

import pandas as pd
import sys 
sys.path.insert(0,'../libs')
#import stanfordnlp
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
import numpy as np
from input_process_util import Processor

#%%
def rule_1(node):
    if node['level']>2 and node['node'].DEPREL == "主谓关系":
        return True
    else:
        return False
    
def rule_2(node):
    if node['level']>1 and node['postag'][0].lower() == "v":
        return True
    else:
        return False

def rule_3(node):
    if node['level']==2 and node['node'].DEPREL != "主谓关系" and node['postag'][0].lower() in ['n','r','a']:
        return True
    else:
        return False
    
def rule_4(node):
    if node['level']>2:
        return True
    else:
        return False
    

def check_all_rules(sentance,analyzer,rule_map):
    check = processor._check_candidate(sentance)
    if check:
        res = base_structure(sentance,analyzer)
        for i in range(1,len(rule_map)+1):
            f_l = res.loop_nodes(res.dep_tree,rule_map[i][0])
            ## check if negation logic, it was set in rules maps
            if rule_map[i][1]:
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
        
#%%
if __name__ == '__main__':
    
    data_path = '../../data/raw/intent_data_clean.csv'
    results_path = '../../data/results/initial_stop_words_analysis.xlsx'
    keep_columns = ['id','用户问句','功能','意图']
    df = pd.read_csv(data_path,encoding='utf8')
    df = df[keep_columns]
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    #df = df.head(1000)
    input_column_name = '用户问句'
    intent_column_name = '意图'    
    processor = Processor(init_stop_words_path='../libs/init_stop_words.txt')
    analyzer = han_analyzer()
    
#%%
    input_data = df[input_column_name].values
    test_data = [i for i in input_data if processor._check_candidate(i)]
    
#%%    
    ## test sentence 
    rule_map = {1: (rule_1,True),
                2: (rule_2,True),
                3: (rule_3,True),
                4: (rule_4,False)}
    
    rule2name = {0: "其他",
                1: "动词+主谓关系",
                2: "动词+并列动词 没有主语",
                3: "动词+名词",
                4: "层数=2"}
#%%
    test = "你相信世界上有鬼吗"
    r = base_structure(test,analyzer).print_dep_tree(print_out=True)
    label = check_all_rules(test,analyzer,rule_map)
    print(label,rule2name[label])
    
#%%
    overall_results = []
    for t in test_data:
        try:
            msg = base_structure(t,analyzer).print_dep_tree(print_out=False)
            msg = '\n'.join(msg) 
            label = check_all_rules(t,analyzer,rule_map)
            name = rule2name[label]
            overall_results.append((t,msg,label,name))
        except:
            print('Something Went Wrong')
            raise Exception(t)
#%%
    df = pd.DataFrame(np.array(overall_results),columns=['input','dependency','label','name'])
    df.to_excel(results_path)
#%%    
#    ## check if it is start with stop words
#    check = processor._check_candidate(test)
#    print(check)
#    if check:
#        res = base_structure(test,analyzer)
#        res.print_dep_tree()
##%%
#    def filter_f(node):
#        if node['level']==2 and node['node'].DEPREL != "主谓关系" and node['postag'][0].lower() in ['n','r','a']:
#            return True
#        else:
#            return False
#        
#    ## check if rule satisfied 
#    f_l = res.loop_nodes(res.dep_tree,filter_f)
#    if len(f_l)>0:
#        #print(processor.remove_init_stop_words(test))
#        for f in f_l:
#            print(f['lemma'],f['node'].POSTAG)