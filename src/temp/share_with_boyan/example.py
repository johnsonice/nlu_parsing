#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 23:27:25 2019

@author: chengyu
"""
import sys
sys.path.insert(0,'./libs')
from long_sentance_process import Long_sentence_processor

#%%
if __name__ == '__main__':
    LP = Long_sentence_processor('./libs/init_stop_words.txt')
    
    ## 例句
    ts = ["可以和我说说你的工作原理是什么吗？", ## 去掉句首 前缀
      "想学点东西，你觉得学什么好",  ## 应该分成两句
      "你会通过什么方式来赚钱",
      "对于XX的前景，你怎么看",    ## 不应该分成两句，前半句不是完整句子
      "能告诉我你的信息在哪里得来的？",
      "我认为你是一个没有什么价值的机器人"] ## 去句首前缀
## 前缀处理
    print('\nInitial stop words process:')

    for t in ts:
        print(LP.ini_processor.check_and_remove_ini(t,LP.analyzer,verbose=False))

## 长句分离 
    print('\nLong sentence processing:')
    for s in ts:
        print(LP.check_and_split(s))
 