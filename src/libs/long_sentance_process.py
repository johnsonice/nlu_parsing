#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:11:39 2019

@author: chengyu
"""

import pandas as pd

import sys 
#sys.path.insert(0,'./libs')
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

def find_levels(node):
    if node['level'] < 5:
        return True
    else:
        return False

    
#%%
if __name__ == '__main__':
    ## set up global variable 
    ## use stanford parser 
    print('parsing using han analyzer....')
    analyzer = han_analyzer()
    processor = Processor('./init_stop_words.txt')

    #%%
    ts = ["可以和我说说你的工作原理是什么吗？",
          "想学点东西，你觉得学什么好",
          "你会通过什么方式来赚钱",
          "对于XX的前景，你怎么看",
          "能告诉我你的信息在哪里得来的？",
          "我认为你是一个没有什么价值的机器人"]
    t = ts[-1]
    t = processor.remove_init_stop_words(t)
    ob = base_structure(t,analyzer)
    ob.print_dep_tree()
    eles = [i for i in ob.loop_nodes(ob.dep_tree,find_levels)]
    
    words = [i['lemma'] for i in sorted(eles,key=lambda i:i['id'])]
    print(t)
    print(words)
    



