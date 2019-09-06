#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
this file will run bi gram and tri gram phrase detection model 
all detected bi and tri grams will be exported for review 
"""
## online training word embedding 
import re
import string
import pandas as pd
import jieba
from gensim.models.phrases import Phrases, Phraser

#%%
def clean(line,punc_list):
    l = line.replace('_',' ')
    l = re.sub(r"[" + re.escape(punc_list) + r"]",'',l)
    l = l.strip()
    
    l = re.sub('[0-9a-zA-Z]+', '', l)
    if len(l)<4:
        return False
    
    return True

def load_and_clean_data():
    ## load all training data
    dat_user = pd.read_csv("../data/dat_real0812.csv")
    dat_simulate = pd.read_csv("../data/df_real_morethan5_sample0812.csv")
    sentances = dat_user['input'].astype(str)
    sentances.append(dat_user['output'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['input'].astype(str),ignore_index=True)
    sentances.append(dat_simulate['output'].astype(str),ignore_index=True)
    sentances.dropna(inplace=True)
    
    ## remove noisy and short sentances
    punc_list = "。，？‘；】【「」、|～！·"+string.punctuation
    print('length of org sentances: {}'.format(len(sentances)))
    sentances_clean = [s for s in sentances if clean(s,punc_list)]
    del sentances
    print('length of cleaned sentances: {}'.format(len(sentances_clean)))
    
    ## tokenize sentances 
    sentances_tokens = [list(jieba.cut(s)) for s in sentances_clean]
    
    return sentances_tokens

#%%
    
if __name__ == "__main__":
    bigram_model_save_path = '../model_weights/bigram_15_20'
    trigram_model_save_path = '../model_weights/trigram_5_10'
    export_path = '../data/phrases_for_review.xlsx'
    
    sentances_tokens= load_and_clean_data()

    # train bigram model 
    print('Working on {}grams...'.format('bi-'))
    bi_phrase = Phrases(sentances_tokens, min_count=10, threshold=20,scoring='default')
    bi_grapm = Phraser(bi_phrase)
    bi_phrase.save(bigram_model_save_path)
    print('bigram model saved at {}'.format(bigram_model_save_path))
    
    # train trigram model 
    print('Working on {}grams...'.format('tri-'))
    bi_sentances_tokens = bi_grapm[sentances_tokens]
    tri_phrase = Phrases(bi_sentances_tokens, min_count=3, threshold=10,scoring='default')
    tri_grapm = Phraser(tri_phrase)
    tri_phrase.save(trigram_model_save_path)
    print('bigram model saved at {}'.format(trigram_model_save_path))

#%%
    print('run one test:')
    sent = list(jieba.cut("我们今天来谈一谈区块链和人工智能的结合"))
    print('origin split: \n {}'.format(sent))
    print('updated split: \n {}'.format(tri_grapm[bi_grapm[sent]]))
#%%
    ## export all phrases to excel for review
    bi_phrases_b = bi_phrase.export_phrases(sentances_tokens)
    tri_phrases_b = tri_phrase.export_phrases(bi_sentances_tokens)
    detected_bi_phrases = list(set([(p.decode('utf-8'),v) for (p,v) in bi_phrases_b]))
    detected_tri_phrases = list(set([(p.decode('utf-8'),v) for (p,v) in tri_phrases_b]))
    detected_tri_phrases = [(p.replace('_',' '),v) for (p,v) in detected_tri_phrases if "_" in p] ## only keep real trigrams
    #%%
    ## incrrase in vocabulary
    bi_phrases_df = pd.DataFrame(detected_bi_phrases,columns=['phrases','score'])
    tri_phrases_df = pd.DataFrame(detected_tri_phrases,columns=['phrases','score'])
    bi_phrases_df.sort_values(by='score',inplace=True,ascending=False)
    tri_phrases_df.sort_values(by='score',inplace=True,ascending=False)
    
    writer = pd.ExcelWriter(export_path)
    bi_phrases_df.to_excel(writer,'bigrams')
    tri_phrases_df.to_excel(writer,'trigrams')
    writer.save()
    print('all detected phrases export to {}'.format(export_path))