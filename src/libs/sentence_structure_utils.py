#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 11:07:55 2019

@author: huang
"""
#import pandas as pd
#
#import sys 
#sys.path.insert(0,'./libs')
#import stanfordnlp
from hanlp_parse import han_analyzer

#sentance_structure_utils
class base_structure(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,sentence,analyzer):
        self.analyzer = analyzer
        self.word_dict,self.word_objs =  self.analyzer.dep_parse(sentence,False)
        self.id2level = self._create_id2level_map()
        self.dep_tree = self.create_dep_tree()
        
    @staticmethod
    def _create_base_dict():
        basic_unit_dict = {'id':None,
                           'level':None,
                           'node': None,
                           'parent_node':None,
                           'lemma': None,
                           'children':[]}
        
        return basic_unit_dict
    
    
    def _create_id2level_map(self):
        id2level = {}
        for i in self.word_objs:
            path_dict,path = self.analyzer.find_path_to_root(i)
            id2level[i.ID] = len(path)-1
        
        return id2level
    
    
    def fill_node_dict(self,word_obj):
        base_node = self._create_base_dict()
        base_node['id'] = word_obj.ID
        base_node['level'] = self.id2level[word_obj.ID]
        base_node['node'] = word_obj
        base_node['parent_node'] = word_obj.HEAD
        base_node['lemma'] = word_obj.LEMMA
        
        children_dict,children = self.analyzer.find_children(self.word_objs,word_obj)
        if children:
            for c in children:
                base_node['children'].append(self.fill_node_dict(c))
        return base_node
        
    def create_dep_tree(self):
        root_dict,root_obj = self.analyzer.find_root(self.word_objs)
        dep_tree = self.fill_node_dict(root_obj)
        
        return dep_tree
    
    @staticmethod
    def _print_node(node,print_out=True):
        message = '{}level{}: {}->[{}]->{}'.format('---'*node['level'],
                                                       node['level'],
                                                       node['lemma'],
                                                       node['node'].DEPREL,
                                                       node['parent_node'].LEMMA)
        if print_out:
            print(message)
        return message
    
    def _flatten(self,L):
        '''(list) -> list
        Returns a flattened version of nested list L
        >>> flatten([1,[2,[3,4]],5])
        [1, 2, 3, 4, 5]
        '''
        # base case: list with one element
        if len(L) == 1:
            if type(L[0]) == list:
                result = self._flatten(L[0])
            else:
                result = L
        elif type(L[0]) == list:
            result = self._flatten(L[0]) + self._flatten(L[1:])
        else:
            result = [L[0]] + self._flatten(L[1:])
        return result
        
        
    def print_dep_tree(self,node=None,print_out=True):
        ## first print root node
        if node is None:
            node = self.dep_tree
        
        msg = []
        msg.append(self._print_node(node,False))
        if len(node['children'])>0:
            for c in node['children']:
                msg.append(self.print_dep_tree(c,False))
        
        msg = self._flatten(msg)
        if print_out:
            print("\n".join(msg))
        
        return msg

        
        
#%%
if __name__ == "__main__":
    test_sentence = "你还能帮我做点啥呢？" 
    analyzer = han_analyzer()
    res = base_structure(test_sentence,analyzer)
    res.print_dep_tree(print_out=True)
    msg = res.print_dep_tree(print_out=False)
