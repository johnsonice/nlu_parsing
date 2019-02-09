#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:02:31 2019

@author: huang
"""
import pandas as pd

import sys 
sys.path.insert(0,'./libs')
#import stanfordnlp
from standfordnlp_parse import stanford_analyzer
from hanlp_parse import han_analyzer

#%%
def get_dep_output(sentence,stand_analyzer):
    try:
        parse_res = stand_analyzer.parse(sentence)[0]
        res = [(i.lemma,i.governor,i.upos,i.dependency_relation)for i in parse_res['tokens']]
    except:
        print(sentence)
        res = None
    return res

def get_dep_output_han(sentence,han_analyser):
    try:
        word_dict, word_objs = han_analyser.dep_parse(sentence,False)  
        res = [(w['LEMMA'],w['POSTAG'],w['DEPREL'],w['HEAD_LEMMA']) for w in word_dict]
    except:
        print(sentence)
        res = None
    return res
#%%
if __name__ == '__main__':
    ## set up global variable 
    data_path = '../data/raw/intent_data_clean.csv'
    results_path = '../data/results/vocab_summary.xlsx'
    co_results_path = '../data/results/co_occurrence_matrix.csv'
    keep_columns = ['id','用户问句','功能','意图']
    df = pd.read_csv(data_path,encoding='utf8')
    df = df[keep_columns]
    df.dropna(inplace=True)
    input_column_name = '用户问句'
    intent_column_name = '意图'

    #%%
    ## use stanford parser 
    print('parsing using stanford analyzer....')
    models_dir = '../models/stanfordnlp_resources'
    lang = 'zh'
    stand_analyzer = stanford_analyzer(models_dir,lang)    
    df['stanford_dep'] = df[input_column_name].apply(get_dep_output,args=(stand_analyzer,))
    
    #%%
    # use hanlp parser
    print('parsing using han analyzer')
    han_analyzer = han_analyzer()
    df['han_dep'] = df[input_column_name].apply(get_dep_output_han,args=(han_analyzer,))
    
    
    #%%
    # export results 
    res_path = '../data/results/dep_res.csv'
    df.to_csv(res_path,encoding='utf8')
    