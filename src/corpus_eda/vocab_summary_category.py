#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 21:54:28 2019

@author: huang
"""

from vocab_summary import *


def do_vocab_analysis(df,data_column='Question',export=True,out_path=None):
    key_tags = ['n','x','v','a','q','d','r','eng','m']
    corpus = df[data_column].values.tolist()
    corpus_clean = [l.lower().strip().replace(" ","") for l in corpus]  ## merge all english words into one
    
    ## get pos tagged data
    corpus_pos = [pos_tag(l) for l in corpus_clean]
    
    # single word analysis
    LEN = len(corpus_pos)
    single_res = single_key_summary(corpus_pos,key_tags=key_tags,total_count=LEN)
    print(single_res['n'].head(10))
    if EXPORT:
        #f_name = os.path.join(corpus_res_folder,out_name)
        export_to_excel(out_path,single_res)
    
    return single_res

#%%

if __name__ =="__main__":
    EXPORT = True
    
    
    ## load and clean data 
    corpus_path = "../../data/raw/corpus/shoulei_9_20.xlsx"
    corpus_res_folder = '../../data/results/corpus'
    #out_file_path = os.path.join(corpus_res_folder,'shoulei_test.xlsx')
    ids = pd.read_excel(corpus_path)['子类名称'].values.tolist()
    
    ## large category vocab analysis
    for ca_id in ids:
        ca_df = pd.read_excel(corpus_path,sheet_name=ca_id)
        out_file_path = os.path.join(corpus_res_folder,'大类','shoulei_{}.xlsx'.format(ca_id))
        res = do_vocab_analysis(ca_df,data_column="问句",export=EXPORT,out_path=out_file_path)
    
    ## small category vocab analysis
    for ca_id in ids:
        ca_df = pd.read_excel(corpus_path,sheet_name=ca_id)
        sub_ids = ca_df['任务子类'].unique()
        for sub_id in sub_ids:
            ca_sub_df = ca_df[ca_df['任务子类']==sub_id]
            out_file_path = os.path.join(corpus_res_folder,'细分类','shoulei_{}_{}.xlsx'.format(ca_id,sub_id))
            res = do_vocab_analysis(ca_sub_df,data_column="问句",export=EXPORT,out_path=out_file_path)
    
    
#    #%%
#    df = pd.read_excel(corpus_path)
#    corpus = df['Question'].values.tolist()
#    corpus_clean = [l.lower().strip().replace(" ","") for l in corpus]  ## merge all english words into one
#    
#    ## get pos tagged data
#    corpus_pos = [pos_tag(l) for l in corpus_clean]
#    
#    # single word analysis
#    LEN = len(corpus_pos)
#    single_res = single_key_summary(corpus_pos,total_count=LEN)
#    print(single_res['n'].head(10))
#    if EXPORT:
#        f_name = os.path.join(corpus_res_folder,'1_token.xlsx')
#        export_to_excel(f_name,single_res)
