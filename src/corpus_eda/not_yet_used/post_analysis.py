#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 22:15:03 2018

@author: chengyu

postag documentation
http://www.hankcs.com/nlp/corpus/several-revenue-segmentation-system-used-set-of-source-tagging.html
https://gist.github.com/luw2007/6016931
https://wenku.baidu.com/view/72b03002eff9aef8941e068e.html

this script is used to create summary statistics for each intent class
"""
import pandas as pd 
import numpy as np
import jieba 
import copy
import jieba.posseg as pseg
from collections import Counter
#import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from scipy.sparse import csr_matrix
dir_dict = "../../data/processed/my_dict.txt"
jieba.load_userdict(dir_dict)

#%%

def dummy_func(doc):
    return doc

def pos_tag(sent):
    res = [ (s,pos) for s,pos in pseg.cut(sent)]
    return res

def get_tag_word(l,tag):
    res = [i[0] for i in l if str.startswith(i[1],tag)]
    res = ' '.join(res)
    return res


def create_class_df(df,cs):
    """
    summarize v n adj words
    """
    c1_df = copy.deepcopy(df[df[intent_column_name] == cs])
    c1_df = c1_df.reset_index()
    del c1_df['index']
    c1_df['v'] = c1_df['tagged_input'].apply(get_tag_word, args=('v',))
    c1_df['n'] = c1_df['tagged_input'].apply(get_tag_word, args=('n',))
    c1_df['a'] = c1_df['tagged_input'].apply(get_tag_word, args=('a',))
    
    sentances = c1_df['tagged_input'].values
    tagged_words_v = Counter([p[0] for li in sentances for p in li if str.startswith(p[1],'v')])
    tagged_words_n = Counter([p[0] for li in sentances for p in li if str.startswith(p[1],'n')])
    tagged_words_a = Counter([p[0] for li in sentances for p in li if str.startswith(p[1],'a')])
    summary_df_v = pd.DataFrame(tagged_words_v.most_common(),columns=['v_w','v_c'])
    summary_df_n = pd.DataFrame(tagged_words_n.most_common(),columns=['n_w','n_c'])
    summary_df_a = pd.DataFrame(tagged_words_a.most_common(),columns=['a_w','a_c'])
    result = pd.concat([c1_df, summary_df_v,summary_df_n, summary_df_a], axis=1, sort=False)
    
    return result

def bow_extractor(corpus,ngram_range=(1,1)):
    
    """
    corpus: should be a document list, when all documents has been tokenized
    """
    bow_transformer = CountVectorizer(
                        analyzer='word',   ## this can actually be any kind of function to preprocess your text
                        tokenizer=dummy_func,
                        preprocessor=dummy_func,
                        token_pattern=None,
                        min_df=1,  ## frequency is at least 1 in overall document
                        ngram_range=ngram_range) ## if it is (1,3) it will consider bi and tri gram as well
    
    features = bow_transformer.fit_transform(corpus) ## does the bow process
    names = bow_transformer.get_feature_names()
    return bow_transformer,features,names

def calculate_cooccurance(X,sparse=False):
    """
    pass in bag of words matrix and calculate co-occurance matrix 
    """
    ## make sure it is an numpy array
    assert type(X) is np.ndarray
    ## calculate co occurance matrix 
    X_mask = copy.copy(X)
    X_mask[X_mask>0] = 1 # convert all counts to be 0 or 1
                         # in this case, we don't care how many times words appears
                         # we only cares if they appear or not in a sentance 
    print('calculating co-occurance matrix')
    if sparse:
        X_mask_sparse = csr_matrix(X_mask)
        Y = csr_matrix.dot(X_mask_sparse.transpose(),X_mask_sparse)
        Y = Y.toarray()
    else:
        Y = np.dot(X_mask.T, X_mask) # calculate co occurance matrix 
    return Y


def get_number(a,b,m,name):
    a_num = name.index(a)
    b_num = name.index(b)
    return m[a_num,b_num]

def word2index(w,name):
    type(w)

#%%
## run one example 
#test = "共享经济很多时候是靠大数据实现的。就像定制机器人用的就是一种比特币的技术。"
#print(list(jieba.cut(test)))
#print(list(pseg.cut(test)))

#%%

if __name__ == "__main__":
    ## set up global variable 
    data_path = '../data/raw/intent_data_clean.csv'
    results_path = '../data/results/vocab_summary.xlsx'
    co_results_path = '../data/results/co_occurrence_matrix.csv'
    df = pd.read_csv(data_path,encoding='utf8')
    df.dropna(inplace=True)
    input_column_name = '用户问句'
    intent_column_name = '意图'
    
    #%% do summary 
    df['tagged_input'] = df[input_column_name].map(pos_tag)
    classes = list(df[intent_column_name].unique())
    ## clean up wrong intent
    classes.remove('国内')
    all_tags = set([t[1] for li in df['tagged_input'].values for t in li])
    
    writer = pd.ExcelWriter(results_path)
    for c in classes:
        #print(c)
        res =  create_class_df(df,c)
        res.to_excel(writer,c)
    writer.save()
    #%%
    #calculate co-occurrence matrix 
    input_tokens = list(df[input_column_name].map(jieba.cut).values)
    bow, features,names = bow_extractor(input_tokens)
    features = features.toarray()
    co_X = calculate_cooccurance(features,sparse=True)
    
    #keep only high frequency verbs
    keep_words_list = ['是','有','会','能','帮','不会','知道','喜欢','做',
                       '觉得','说','赚钱','推销','卖','销售','要','买',
                       '需要','想','懂','学习','工作','购买','到']
    keep_indexes = [names.index(w) for w in keep_words_list]
    keep_co_X = co_X[:,keep_indexes]
    ## export matrix to csv
    df_co = pd.DataFrame(keep_co_X,columns=keep_words_list,index=names)
    df_co = df_co.sort_values(by=keep_words_list,ascending=False)
    df_co.to_csv(co_results_path,encoding='utf-8')