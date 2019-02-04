#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 21:54:23 2019

@author: chengyu
"""

## for tag descriptions 
## https://github.com/hankcs/HanLP/blob/master/data/dictionary/other/TagPKU98.csv
from pyhanlp import *


class han_analyzer(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self):
        CRFLexicalAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")
        self.CRF_analyzer = CRFLexicalAnalyzer()
        self.parseDependency = HanLP.parseDependency
        self.CoNLLWord = JClass("com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLWord")
    
    def _w2d(self,word_obj):
        """turn hanlp word object to dictionary for easy reading"""
        w = dict()
        w['ID'] = word_obj.ID
        w['POSTAG'] = word_obj.POSTAG
        w['DEPREL'] = word_obj.DEPREL
        
        w['LEMMA'] = word_obj.LEMMA
        if word_obj.HEAD:
            w['HEAD_LEMMA'] = word_obj.HEAD.LEMMA
        else:
            w['HEAD_LEMMA'] = None
        return w
        
    def _print_dep(self,words):
        assert isinstance(words,list) 
        for word in words:  # 通过dir()可以查看sentence的方法
            print("%s %s %s --(%s)--> %s" % (word['ID'], 
                                              word['LEMMA'], 
                                              word['POSTAG'], 
                                              word['DEPREL'], 
                                              word['HEAD_LEMMA']))
    def _print_path(self,words):
        assert isinstance(words,list)
        for word in words:
            print("%s --(%s)--> " % (word['LEMMA'], word['DEPREL']))
        
    def dep_parse(self,sentence,nice_print=False):
        res = self.parseDependency(sentence)
        word_objs = [w for w in res.iterator()]
        word_dict = [self._w2d(w) for w in word_objs]
        if nice_print:
            self._print_dep(word_dict)
        return word_dict,word_objs
    
    def find_root(self,word_objs):
        for w in word_objs:
            if w.HEAD == self.CoNLLWord.ROOT:
                return self._w2d(w),w
        return None
        
    def find_children(self,word_objs,parent_obj):
        """
        parent_obj must be a word object
        return: a list of word dict and word objects
        """
        children = list()
        for w in word_objs:
            if w.HEAD == parent_obj:
                children.append(w)
        if len(children)>0:
            children_dict = [self._w2d(w) for w in children]

            return children_dict,children
        else:
            raise Exception('parent object not in sentance: {}'.format(parent_obj.LEMMA))
            
    def find_path_to_root(self,word_obj,nice_print=False):
        """
        given any node, find all elements to root
        """
        path = [word_obj]
        head = word_obj
        while head.HEAD:
            head=head.HEAD
            if (head == self.CoNLLWord.ROOT):
                path.append(head)
                path_dict = [self._w2d(w) for w in path]
                if nice_print:
                    self._print_path(path_dict)
                return path_dict,path
            else:
                path.append(head)
#%%
            
if __name__ == "__main__":
    analyzer = han_analyzer()
    
    test = "上海华安工业公司董事长谭旭光和秘书胡花蕊来到美国纽约现代艺术博物馆参观"
    print(test)
    ## parse and print dependency
    word_dict, word_objs = analyzer.dep_parse(test,True)      
    print('\n {}'.format(word_dict))
    ## find root of parsed sentence
    root_w,root = analyzer.find_root(word_objs)
    print("\nroot: {}".format(root_w))
    
    ## find children of a node
    children_dict,children = analyzer.find_children(word_objs,root)
    print("\nChildren of root node:{}".format(children_dict))

    ## find path to root 
    path_dict,path = analyzer.find_path_to_root(word_objs[0],nice_print=True)
    print("\npath to root: {}".format(path_dict))