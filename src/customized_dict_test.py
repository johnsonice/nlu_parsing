#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 12:13:39 2019

@author: huang
"""

from pyhanlp import *
import sys 
sys.path.insert(0,'./libs')
from hanlp_parse import han_analyzer
analyzer = han_analyzer()
#%%

if __name__ == "__main__":
    """
    to add customized dictionary 
    add new words to customizedDict.txt file 
    to find whhere it is, use HanLP.Config.CoreDictionaryPath
    this is the corenaturedictionary 
    customized dictionary is in the same directury 
    """
    
    ## check dictionary path
    core_dir = os.path.join(os.path.dirname(HanLP.Config.CoreDictionaryPath),'custom')
    custom_dict_path = os.path.join(core_dir,'CustomDictionary.txt')
    assert os.path.exists(custom_dict_path)
    print(custom_dict_path)

    ## test one sentence 
    text = "你有没有卖复古款钱包？"
    print(HanLP.segment(text))
    words, objs = analyzer.dep_parse(text)
    print(words)