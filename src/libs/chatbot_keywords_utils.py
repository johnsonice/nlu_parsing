#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 11:06:18 2019

@author: huang
"""

import pandas as pd
import jieba 
#%%
def read_keywords(data_path,key='token',val='weight'):
    df = pd.read_csv(data_path,header=1)
    df = df[[key,val]]
    df.drop_duplicates(inplace=True)
    key_dict = pd.Series(df[val].values,index=df[key]).to_dict()
    return key_dict

def get_weights(input_list,key_dict):
    '''get weights for each input words, if in key list, weights > 1'''
    matched_dict = [(k,key_dict.get(k,1)) for k in input_list]
    return matched_dict

#%%
    
if __name__=="__main__":
    data_path = "../../data/raw/chatbot_keywords.csv"
    key_dict = read_keywords(data_path)
    print(key_dict.get('not in dictionary',1))
    print(key_dict.get('正确'))
    
    input_list = list(jieba.cut('你的名字叫什么？'))
    print(get_weights(input_list,key_dict))
