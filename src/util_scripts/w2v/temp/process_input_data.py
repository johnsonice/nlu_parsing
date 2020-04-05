#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 20:00:43 2020

@author: chengyu
"""

import os
os.chdir('/home/chengyu/Dev/All_chatbot_models/nlu_parsing/data/W2v/training_data')
from corpus import CORPUS
import pandas as pd
import string
import re

#%%

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
    
    ## process py data
    Qs = [i['Questions'] for i in CORPUS]
    As = [i['Answers'] for i in CORPUS]
    data = pd.DataFrame(Qs + As)
    data.to_csv('w2v_train.csv',header=False,index=False)
    
    ## process old chat data
    dat_user = pd.read_csv("./inputs/dat_real0812.csv")
    dat_simulate = pd.read_csv("./inputs/df_real_morethan5_sample0812.csv")
    sentances = dat_user['input'].astype(str)
    sentances.append(dat_user['output'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['input'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['output'].astype(str),ignore_index=True)
    sentances.dropna(inplace=True)
    
    punc_list = "。，？‘；】【「」、|～！·"+string.punctuation
    print('length of org sentances: {}'.format(len(sentances)))
    sentances_clean = [s for s in sentances if clean(s,punc_list)]
    data2 = pd.DataFrame(sentances_clean)
    data2.to_csv('./w2v_train_old.csv',header=False,index=False)
    #%%
    data_merge= data.append(data2,ignore_index=True)
    data_merge.to_csv('./w2v_train_merge.csv',header=False,index=False)
    
    
    
    