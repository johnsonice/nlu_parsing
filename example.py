#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 22:21:28 2019

@author: huang
"""

## example 

import sys 
import os 
try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
except:
    dir_path = '.'
sys.path.insert(0,os.path.join(dir_path,'src'))
from match_answer import RB2


if __name__ == "__main__":
    ## input premeters
    #kb_path = "./data/raw/knowledge_input.xlsx"
    kb_path = "./data/raw/victor_knowledge_input.xlsx"
    init_stop_words_path = './src/libs/init_stop_words.txt'
    chatbot_keywords_path = "./data/raw/chatbot_keywords.csv"
    nlu = RB2(kb_path,init_stop_words_path,chatbot_keywords_path)
    #%%
    # run one example 
    test_sentence= "你能说说伦敦的房地产怎么样么"
    ans = nlu.match(test_sentence,deep_match=True,match_intent=False,topn=1,check_long_sentence=True)   
    print(ans)
#%%
    ## evaluate an input pattern and a input asking sentence 
    input_pattern = '<set>Victor</set>#<set>可以</set>#<set>描述</set>#'
    #input_pattern=None
    res = nlu.evaluate_pattern(test_sentence,input_pattern)
    print(res)
    
    