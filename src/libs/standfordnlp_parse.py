#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 13:53:56 2019

@author: chengyu
"""

import stanfordnlp
#stanfordnlp.download('zh','~/stanfordnlp_resources',confirm_if_exists=True) ## first time load is going to take some time 

class stanford_analyzer(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,models_dir,lang='zh',use_gpu=False):
        print('Building pipeline...')
        self.nlp = stanfordnlp.Pipeline(models_dir=models_dir,lang=lang,use_gpu=use_gpu) 
    
    def _sentence_output(self,sent_obj):
        """
        only output word dict,tokens and dependency tree
        """
        words_dict = {t.index:t.words[0] for t in sent_obj.tokens}
        tokens = sent_obj.words
        dep_tree = sent_obj.dependencies
        res = {'words_dict':words_dict,
               'tokens':tokens,
               'dep_tree': dep_tree}
        return res
    
    def _get_level(self,parse_res):
        """
        return a map from governor to level, index start from 1
        """
        governors = [i.governor for i in parse_res['tokens']]
        governors = set(governors)
        gov2lev = {i:idx+1 for idx,i in enumerate(governors)}
        return gov2lev
           
    def parse(self,text):
        doc = self.nlp(text)
        res = [self._sentence_output(s) for s in doc.sentences]
        return res
            
    def filter_by_dep_ele(self,tokens,dep_ele=['root'],mode='keep'):
        if mode == 'keep':
            res = [i for i in tokens if i.dependency_relation in dep_ele]
        elif mode == 'drop':
            res = [i for i in tokens if not i.dependency_relation in dep_ele]
        else:
            raise Exception('mode must be keep or drop')
            
        if len(res)==0:
            print('No results found')
            return None
        else:
            return res 
        
    def filter_by_level(self,parse_res,levels=[1],mode='keep'):
        
        gov2lev = self._get_level(parse_res)
        
        if mode == 'keep':
            res = [t for t in parse_res['tokens'] if gov2lev[t.governor] in levels]
        elif mode == 'drop':
            res = [t for t in parse_res['tokens'] if not gov2lev[t.governor] in levels]
        else:
            raise Exception('mode must be keep or drop')
            
        if len(res)>0:
            return res
        else:
            print('No results found')
            return None
   
    def simplify_results(self,tokens,simple_print=False):
        res = [(i.lemma,i.upos,i.dependency_relation) for i in tokens]
        if simple_print:
            print(res)
        return res


#%%
if __name__ == "__main__":
    
    ## load model 
    models_dir = '../models/stanfordnlp_resources'
    lang = 'zh'
    analyzer = stanford_analyzer(models_dir,lang)    
    
    ## run one test
    test = "你有些什么功能呢？"
    print(test)
    parse_res =analyzer.parse(test)[0]
    
    #################################
    ## some filter functionalities ##
    #################################
    
    ## filter by dependency tag
    ws = analyzer.filter_by_dep_ele(parse_res['tokens'],['root','nsubj'],mode='keep')
    print(ws)
    
    ## filter by tree level
    ws = analyzer.filter_by_level(parse_res,levels=[1,2])
    print(ws)
    
    ## prety print and simple results for export 
    ws= analyzer.simplify_results(parse_res['tokens'],simple_print=True)
        