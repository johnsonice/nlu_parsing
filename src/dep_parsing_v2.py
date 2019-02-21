#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 16:15:40 2019

@author: chengyu
"""

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
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
import numpy as np
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

if __name__ == '__main__':
    ## set up global variable 
    data_path = '../data/raw/intent_data_clean.csv'
    results_path = '../data/results/dep_tree_v2.xlsx'
    keep_columns = ['id','用户问句','功能','意图']
    df = pd.read_csv(data_path,encoding='utf8')
    df = df[keep_columns]
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    #df = df.head(1000)
    input_column_name = '用户问句'
    intent_column_name = '意图'
    #%%
    ## use stanford parser 
    print('parsing using han analyzer....')
    analyzer = han_analyzer()
    processor = Processor('./libs/init_stop_words.txt')
    input_data = df[input_column_name].values
    #%%
    test_data = [processor.remove_init_stop_words(i) for i in input_data]
    assert len(test_data)==len(input_data)
    df['filtered_input'] = np.array(test_data)
    #%%
    msg_list = [base_structure(s,analyzer).print_dep_tree(print_out=False) for s in test_data]
    msg_list = ['\n'.join(m) for m in msg_list]
    #%%
    df['han_dep'] = df[input_column_name].apply(get_dep_output_han,args=(analyzer,))
    df['han_dep_tree'] = np.array(msg_list)
    #%%
    df.to_excel(results_path)