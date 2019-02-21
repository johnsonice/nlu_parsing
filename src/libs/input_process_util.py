#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 20:57:30 2019

@author: huang
"""
import re


class Processor(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,init_stop_words_path='init_stop_words.txt'):
        self.init_stop_words = self.read_text(init_stop_words_path)
        
    @staticmethod
    def read_text(file_path):
        with open(file_path, "r") as f:
            input_list = f.readlines()
            input_list = [i.strip('\n').strip() for i in input_list]
        return input_list
    
    
    def remove_init_stop_words(self,input_sentance,verbose=True):
        
        stop_words = self.init_stop_words
        
        if len(input_sentance)==0:
            if verbose:
                print('warning: input sentence is empty')
            return input_sentance
        
        for sw in stop_words:
            res = re.search(sw,input_sentance)
            if res is None:
                continue
            elif res.start() == 0:
                if verbose:
                    print("[{}] removed from: {}.".format(sw,input_sentance))
                return input_sentance.replace(sw,'')
            else:
                continue
        
        return input_sentance


#%%
if __name__=="__main__":
    processor = Processor(init_stop_words_path='init_stop_words.txt')
    
    test = "你知道这个世界上有外星人么？"
    print(processor.remove_init_stop_words(test))