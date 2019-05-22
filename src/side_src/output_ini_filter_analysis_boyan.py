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

def get_matched_rules(sentence,processor,analyzer):
    check = processor.check_all_rules(sentence,analyzer)
    return processor.rule2name[check]

#%%
if __name__ == '__main__':
    
    data_path = '../../data/raw/sentence_with_prefix'
    results_path = '../../data/results/initial_stop_words_analysis_boyan.xlsx'
    
    #%%
    df = pd.read_csv(data_path,header=None,names=['sentence'])
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    #%%
    input_column_name = 'sentence' 
    processor = Processor(init_stop_words_path='../libs/init_stop_words.txt')
    analyzer = han_analyzer()
    #%%
    df['remove_candidate'] = df[input_column_name].apply(processor._check_candidate)
    df['matched_rules'] = df[input_column_name].apply(get_matched_rules,args=(processor,analyzer,))
    df['results'] = df[input_column_name].apply(processor.check_and_remove_ini,args=(analyzer,False))   
    df.to_excel(results_path)
 
