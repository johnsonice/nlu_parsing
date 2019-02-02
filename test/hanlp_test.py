#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 21:08:15 2019

@author: chengyu
"""

from pyhanlp import *

#%%

test = "你说说你还有什么功能？"
test = "今天我要去杭州开会，3.00 走"
print(HanLP.segment(test))
#%%
document = "水利部水资源司司长陈明忠9月29日在国务院新闻办举行的新闻发布会上透露，" \
           "根据刚刚完成了水资源管理制度的考核，有部分省接近了红线的指标，" \
           "有部分省超过红线的指标。对一些超过红线的地方，陈明忠表示，对一些取用水项目进行区域的限批，" \
           "严格地进行水资源论证和取水许可的批准。"
print(HanLP.extractKeyword(document, 10))
print(HanLP.extractSummary(document, 3))
#%%
sentence = HanLP.parseDependency(test)
methods = dir(sentence)
print(methods)
for word in sentence.iterator():  # 通过dir()可以查看sentence的方法
    print("%s %s %s --(%s)--> %s" % (word.LEMMA, word.ID, word.POSTAG, word.DEPREL, word.HEAD.LEMMA))
print()

# 也可以直接拿到数组，任意顺序或逆序遍历
word_array = sentence.getWordArray()
for word in word_array:
    print("%s --(%s)--> %s" % (word.LEMMA, word.DEPREL, word.HEAD.LEMMA))
print()

print(len(word_array))
#%%
# 还可以直接遍历子树，从某棵子树的某个节点一路遍历到虚根
CoNLLWord = JClass("com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLWord")
head = word_array[6]
while head.HEAD:
    head = head.HEAD
    if (head == CoNLLWord.ROOT):
        print(head.LEMMA)
    else:
        print("%s --(%s)--> " % (head.LEMMA, head.DEPREL))
#%%

attrs = vars(HanLP._proxy)
print(attrs.keys())

#%%
## perception lexical analyzer
PerceptronLexicalAnalyzer = JClass('com.hankcs.hanlp.model.perceptron.PerceptronLexicalAnalyzer')
analyzer = PerceptronLexicalAnalyzer()
print(analyzer.analyze("上海华安工业（集团）公司董事长谭旭光和秘书胡花蕊来到美国纽约现代艺术博物馆参观"))
#%%
CRFLexicalAnalyzer = JClass("com.hankcs.hanlp.model.crf.CRFLexicalAnalyzer")
analyzer = CRFLexicalAnalyzer()
print(analyzer.analyze(test))