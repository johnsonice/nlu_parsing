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
sys.path.insert(0,'../libs')
#import stanfordnlp
from hanlp_parse import han_analyzer
from sentence_structure_utils import base_structure
import numpy as np
from input_process_util import Processor
from request_util import get_intent
#%%

if __name__ == '__main__':
    ## set up global variable 
    data_path = './data/dependency_tree_test_data.xlsx'
    results_path = './data/intents_out.xlsx'
    keep_columns = ['ask']
    df = pd.read_excel(data_path,sheet_name='a_b_2')
    df = df[keep_columns]
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    #df = df.head(1000)
    input_column_name = 'ask'
    #intent_column_name = '意图'
    #%%
    ## use stanford parser 

    input_data = df[input_column_name].values
    intents = [get_intent(i)['text']['lv2']['label'] for i in input_data]
    df['filtered_input'] = np.array(intents)
    #df.to_excel(results_path)