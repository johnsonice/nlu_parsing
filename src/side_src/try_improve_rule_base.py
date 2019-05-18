#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 14:47:04 2019

@author: chengyu
"""

import pandas as pd
import sys 
sys.path.insert(0,'../libs')
#import stanfordnlp
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
from knowledge_bank_utils import get_intent_classes
import numpy as np
from input_process_util import Processor
#%%
init_stop_words_path = '../libs/init_stop_words.txt'
data_path = '../../data/results/filtered_test0424.xlsx'
out_data_path = '../../data/results/filtered_test_nlu_0424.xlsx'
#results_path = '../../data/results/.xlsx'
df = pd.read_excel(data_path,'wenti')
qs = df['问题']

#%%
processor = Processor(init_stop_words_path=init_stop_words_path)
analyzer = han_analyzer()
#%%

## step one 
df ['ini_remove'] = df['问题'].apply(processor.check_and_remove_ini,args=(analyzer,False))
#%%
intents = [get_intent_classes(i) for i in qs]
#%%
df_intents = pd.DataFrame(intents)
#%%

df = df.merge(df_intents, left_index=True, right_index=True)
#%%
out_data_path = '../../data/results/filtered_test_nlu_0424.xlsx'
df.to_excel(out_data_path)
