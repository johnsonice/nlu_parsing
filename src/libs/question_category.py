#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 21:27:35 2019

@author: chengyu
"""

import jieba 
import jieba.posseg as jieba_pos_tagger
import pandas as pd
import collections
import re
#%%
def get_sentence_vs(user_input):
    pos_generator = jieba_pos_tagger.cut(user_input)
    pos_lst = [(w.word, w.flag) for w in pos_generator]
    v_lst = [item[0] for item in pos_lst if item[1] in ['v', 'vd', 'vg', 'vq']]
    q_list = [item[0] for item in pos_lst if item[1] in ['q']]
    a_list = [item[0] for item in pos_lst if item[1] in ['a', 'ad', 'ag', 'an']]
    return v_lst,q_list,a_list

def _flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from _flatten(el)
        else:
            yield el

def get_all_vs(data_path = "../../data/raw/vocab/intent_data_clean.csv"):
    
    dat = pd.read_csv(data_path)
    user_input = dat['用户问句']
    vocabs = [get_sentence_vs(u) for u in user_input if len(get_sentence_vs(u))>0]
    v_s = list(set(list(_flatten([i[0] for i in vocabs]))))
    q_s = list(set(list(_flatten([i[1] for i in vocabs]))))
    a_s = list(set(list(_flatten([i[2] for i in vocabs]))))
#    vs = list(_flatten(vs))
#    vs = list(set(vs))
    return v_s,q_s,a_s

#
#### produce a vocabulary list
#v_lst,q_list,a_list = get_all_vs()
##%%
#with open('../../data/processed/verbs.txt', 'w') as filehandle:
#    for v in v_lst:
#        filehandle.write('%s\n' % v)
#with open('../../data/processed/qs.txt', 'w') as filehandle:
#    for v in q_list:
#        filehandle.write('%s\n' % v)
#with open('../../data/processed/adjs.txt', 'w') as filehandle:
#    for v in a_list:
#        filehandle.write('%s\n' % v)
#%%
class Question_Classifier(object):
    """
    rule based question type classifier
    """
    def __init__(self,verbs_path='verbs.txt',qs_path ='qs.txt',adjs_path='adjs.txt'):
        self.verbs = self.read_vocabs(verbs_path)
        self.qs = self.read_vocabs(qs_path)
        self.adjs = self.read_vocabs(adjs_path)
        self.rules = self.specify_rules()
        

    def read_vocabs(self,verbs_path):
        with open (verbs_path, 'r') as f:
            v_list =  f.readlines()
            v_list = [v.strip('\n') for v in v_list]
        return v_list

    def specify_rules(self):
        v_lst = self.verbs
        q_lst = self.qs
        a_lst = self.adjs
        
        rules = {}
        # 是非
        rules['sf_rule_1'] = [v+'不'+v for v in v_lst]  # v不v
        rules['sf_rule_2']= [v+'(没有|没)'+v for v in v_lst]  # v没有/没v
        rules['sf_rule_3'] = [v+'.*(没有|没|不)(\\?|？)$' for v in v_lst]  # v...不/没/没有？
        rules['sf_rule_4'] = [v+'.+(没有|没|不)'+v for v in v_lst]  # v...不/没/没有v？
        rules['sf_rule_5'] = "(吗|吗？|吗\\?)$"
        rules['sf_rule_6'] = "(吧|吧？|吧\\?)$" 
        #选择
        rules['xz_rule_1'] = ".+还是.+"
        # 特殊
        rules['ts_rule_1'] = "(什么|啥)(\\?|？|)$"  # 什么/啥
        rules['ts_rule_2'] = "(?<!为)什么.+"  # 什么 + 名词短语
        rules['ts_rule_3'] = "谁"   # 谁
        rules['ts_rule_4'] = "(哪里|哪儿|哪)$"   # 哪里/哪儿/哪
        rules['ts_rule_5'] = ['哪'+q for q in q_lst]   # 哪+量词+名词
        rules['ts_rule_6'] = ['怎么'+v for v in v_lst]  # 怎么+v
        rules['ts_rule_7'] = '为什么'   # 为什么
        rules['ts_rule_8'] = '多少'  # 多少
        rules['ts_rule_9'] = ['多'+a for a in a_lst]  # 多+形容词
        
        return rules
    
    ##### 这code写的太差了 #######
    ##### 暂时县这样吧 ##########
    def classify(self,sentence):
        if True in [re.search(rule, sentence) is not None for rule in self.rules['sf_rule_1']]:
            query_class_1 = '是非问句'
            query_class_2 = 'v不v'
        elif True in [re.search(rule, sentence) is not None for rule in self.rules['sf_rule_2']]:
            query_class_1 = '是非问句'
            query_class_2 = 'v没有/没v'
        elif True in [re.search(rule, sentence) is not None for rule in self.rules['sf_rule_3']]:
            query_class_1 = '是非问句'
            query_class_2 = 'v...不/没/没有？'
        elif True in [re.search(rule, sentence) is not None for rule in self.rules['sf_rule_4']]:
            query_class_1 = '是非问句'
            query_class_2 = 'v...不/没/没有v？'
        elif re.search(self.rules['sf_rule_5'], sentence) is not None:
            query_class_1 = '是非问句'
            query_class_2 = '吗？'
        elif re.search(self.rules['sf_rule_6'], sentence) is not None:
            query_class_1 = '是非问句'
            query_class_2 = '吧？'
        elif re.search(self.rules['xz_rule_1'], sentence) is not None:
            query_class_1 = '选择问句'
            query_class_2 = 'A还是B'
        elif re.search(self.rules['ts_rule_1'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '什么/啥'
        elif re.search(self.rules['ts_rule_2'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '什么+名词短语'
        elif re.search(self.rules['ts_rule_3'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '谁'
        elif re.search(self.rules['ts_rule_4'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '哪里/哪儿/哪'
        elif True in [re.search(rule, sentence) is not None for rule in self.rules['ts_rule_5']]:
            query_class_1 = '特殊问句'
            query_class_2 = '哪+量词+名词'
        elif True in [re.search(rule, sentence) is not None for rule in self.rules['ts_rule_6']]:
            query_class_1 = '特殊问句'
            query_class_2 = '怎么+v'
        elif re.search(self.rules['ts_rule_7'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '为什么'
        elif re.search(self.rules['ts_rule_8'], sentence) is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '多少'   
        elif [re.search(rule, sentence) is not None for rule in self.rules['ts_rule_9']] is not None:
            query_class_1 = '特殊问句'
            query_class_2 = '多+形容词'
        else:
            query_class_1 = '其他'
            query_class_2 = '其他'
        
        return query_class_1, query_class_2

#%%
if __name__ == "__main__":
    v_path = '../../data/processed/verbs.txt'
    q_path = '../../data/processed/verbs.txt'
    a_path = '../../data/processed/verbs.txt'
    QC = Question_Classifier(v_path,q_path,a_path)
    
    example_questions = ['哪笔交易？','你起床没起床？',
                         '你计较没有？','说说今天股市涨不涨']
    for q in example_questions:
        print(QC.classify(q))
    
