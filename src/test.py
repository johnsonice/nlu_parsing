#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 16:15:40 2019

@author: chengyu
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:02:31 2019

@author: huang
"""
import pandas as pd

import sys 
sys.path.insert(0,'./libs')
#import stanfordnlp
from standfordnlp_parse import stanford_analyzer
from hanlp_parse import han_analyzer
from collections import defaultdict
import numpy as np
#%%

def get_dep_output_han(sentence,han_analyser):
    try:
        word_dict, word_objs = han_analyser.dep_parse(sentence,False)  
        res = [(w['LEMMA'],w['POSTAG'],w['DEPREL'],w['HEAD_LEMMA']) for w in word_dict]
    except:
        print(sentence)
        res = None
    return res

def flat_dictionary(record_dict,keys=[],values=[]):
    for k,v in record_dict.items():
        keys.append(k)
        values.append(v['value'])
        if v.get('subnodes'):
            flat_dictionary(v['subnodes'],keys,values)
        
        assert len(keys) == len(values)
    return keys,values

def convert_record2df(record_list):
    columns,_ = flat_dictionary(record_list[0],keys=[],values=[])
    values = [flat_dictionary(r,keys=[],values=[])[1] for r in record_list]
    df_values = np.array(values)
    df = pd.DataFrame(df_values,columns=columns)
    return df

def record_func():
    """
    factory function to generate empty dictionary
    
    """
    res = {
            "主语":{"value":None,
                 'look_up':['主谓关系'],
                 'subnodes':{"修饰":{'value':None,
                                   'look_up':['定中关系']
                                   }
                            }
                  },
            "核心":{"value":None,
                    'look_up':['核心关系'],
                    'subnodes':{"兼语":{'value':None,
                                      'look_up':['兼语']
                                      },
                                "状中":{'value':None,
                                      'look_up':['状中结构']
                                      },
                                "间宾":{'value':None,
                                      'look_up':['间宾关系']
                                      }
                                }
                    },
            "宾语":{"value":None,
                    'look_up':['动宾关系'],
                    'subnodes':{
                            "定中":{'value':None,
                                    'look_up':['定中关系']},
                            "状中":{'value':None,
                                    'look_up':['状中结构']  }
                            }
                    }

            }
    return res

def _loop_assign_dict(obj_dict,objs_list,analyzer,exclude=['核心']):
    for k,v in obj_dict.items():
        if k in exclude:
            continue
        look_up_element_list = v['look_up']
        wd, wj = analyzer.filter_by_dep_ele(objs_list,look_up_element_list,verbose=False)
        if wd:
            v['value'] = " ".join([w.LEMMA for w in wj])
            v['obj'] = wj
    return obj_dict
     
def fill_in_dict(sentence,record_obj,analyzer):
    """
    first role to fill in blanks 
    """
    word_dict, word_objs = analyzer.dep_parse(sentence,False)  
    root_dict,root_obj = analyzer.find_root(word_objs)
    if not root_dict:
        raise Exception('No root fund for the sentence:{}'.format(sentence))
    
    root_childrens_dict, root_childrens = analyzer.find_children(word_objs,root_obj)
    record_obj['核心']['value'] = root_obj.LEMMA
    record_obj['核心']['obj'] = [root_obj]
    try:
        if root_childrens:
            _loop_assign_dict(record_obj,root_childrens,analyzer,exclude=['核心'])
        for k,v in record_obj.items():
            if v['value']:
                subnode_children_obj_list = []
                for i in v['obj']:
                    subnode_children_dict, subnode_children_obj= analyzer.find_children(word_objs,i)
                    if subnode_children_obj:
                        subnode_children_obj_list.extend(subnode_children_obj)
                if len(subnode_children_obj_list)>0:
                    _loop_assign_dict(record_obj[k]['subnodes'],subnode_children_obj_list,analyzer,exclude=[])
    except Exception as e:
        print(sentence)
        print(word_dict)
        raise Exception(e)
    return record_obj

#%%
if __name__ == '__main__':
    ## set up global variable 
    data_path = '../data/raw/intent_data_clean.csv'
    results_path = '../data/results/vocab_summary.xlsx'
    co_results_path = '../data/results/co_occurrence_matrix.csv'
    keep_columns = ['id','用户问句','功能','意图']
    df = pd.read_csv(data_path,encoding='utf8')
    df = df[keep_columns]
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    input_column_name = '用户问句'
    intent_column_name = '意图'
    #%%
    ## use stanford parser 
    print('parsing using han analyzer')
    han_analyzer = han_analyzer()
    test_data = df[input_column_name].values
    record_list = [fill_in_dict(t,record_func(),han_analyzer) for t in test_data]
    #%%
    df_merge = convert_record2df(record_list)
    #%%
    # use hanlp parser
    df['han_dep'] = df[input_column_name].apply(get_dep_output_han,args=(han_analyzer,))
    #%%
    df = df.join(df_merge)
    #%%
    # export results 
    res_path = '../data/results/dep_structure.csv'
    df.to_csv(res_path,encoding='utf8')
#%%
#    test = "你多大了？"
#    x = fill_in_dict(test,record_func(),han_analyzer)
#    x