#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 19:40:20 2020

@author: chengyu
"""
import re
import pandas as pd
import string
import jieba

# define global veriable
punc_list = "。，？‘；】【「」、|～！·"+string.punctuation


def clean(line,punc_list):
    """"
    Simple clearn text
    """
    l = line.replace('_',' ')
    l = re.sub(r"[" + re.escape(punc_list) + r"]",'',l)
    l = l.strip()
    
    l = re.sub('[0-9a-zA-Z]+', '', l)
    if len(l)<4:
        return False
    
    return True




if __name__ == "__main__":
    ## load all training data
    data_folder = 
    dat_user = pd.read_csv("../data/dat_real0812.csv")
    dat_simulate = pd.read_csv("../data/df_real_morethan5_sample0812.csv")
    sentances = dat_user['input'].astype(str)
    sentances.append(dat_user['output'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['input'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['output'].astype(str),ignore_index=True)
    sentances.dropna(inplace=True)
    #%%
    ## remove noisy and short sentances
    
    print('length of org sentances: {}'.format(len(sentances)))
    sentances_clean = [s for s in sentances if clean(s,punc_list)]
    del sentances
    print('length of cleaned sentances: {}'.format(len(sentances_clean)))
    
    ## tokenize sentances 
    sentances_tokens = [list(jieba.cut(s)) for s in sentances_clean]
    