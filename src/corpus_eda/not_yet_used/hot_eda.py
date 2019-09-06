
# ================================================================
# This program extracts key words from HoT Q&A template and actual    
# bot testing data/corpus, by their POS. 
#       last update on 6/16/2019
# ================================================================


#%%
import pandas as pd
import jieba 
import jieba.posseg as jieba_pos_tagger
import jieba.analyse
import re
import time
import os
from datetime import datetime


#%%
dir_path = './data/'

#%%
dat_temp = pd.read_excel(os.path.join(dir_path, "HoT_corpus.xlsx"), sheet_name = "知识边界")
dat_user = pd.read_excel(os.path.join(dir_path, "HoT_corpus.xlsx"), sheet_name = "测试数据")

#%%
dat_temp['source'] = '模板'
dat_user['source'] = '实际测试'

dat_full = pd.concat([dat_temp, dat_user])

dat_full['用户问句'].str.strip()
dat_full['机器人答句'].str.strip()

#%%
print('before deduplication:' + str(dat_full.shape))

dat_full.drop_duplicates

print('after deduplication:' + str(dat_full.shape))

#%%
# replace unanswered template
dat_full['机器人答句'] = ['' if string == '【需要伦敦团队提供】' else string for string in dat_full['机器人答句']]

#%%
# text of questions from template 
txt_temp_q = "".join([str(txt) for txt in dat_temp['用户问句'].values.tolist()])

# text of answers from template 
txt_temp_a = "".join([str(txt) for txt in dat_temp['机器人答句'].values.tolist()])

# text of questions from template 
txt_user_q = "".join([str(txt) for txt in dat_user['用户问句'].values.tolist()])

# text of answers from template 
txt_user_a = "".join([str(txt) for txt in dat_user['机器人答句'].values.tolist()])


#%%
jieba.load_userdict(os.path.join(dir_path, "hot_dict.txt"))

#%%
seg_lst_temp_q = jieba.cut_for_search(txt_temp_q)
seg_lst_temp_a = jieba.cut_for_search(txt_temp_a)
seg_lst_user_q = jieba.cut_for_search(txt_user_q)
seg_lst_user_a = jieba.cut_for_search(txt_user_a)

#%%
print("/ ".join(seg_lst_user_a))

#%%

def extract_keywords(text, top_n_noun, top_n_verb, top_n_adj, source, comp):
    """Function to extract keywords from Chinese corpus and output them into a dataframe.

    Args:
        text (str): The corpus to extract key words from.
        top_n_noun (int): The max number of nouns to extract.
        top_n_verb (int): The max number of verbs to extract.
        top_n_adj (int): The max number of adjectives to extract.
        source (str): from HoT template QA or actual/test QA data
        comp (str): the component this corpus belongs to in the dialogue (i.e. Q or A)

    Returns:
        df_final: A dataframe lists the key words, their POS, source, and the component it belongs to in the corpus (i.e. Q or A) 

    """
    kw_n = jieba.analyse.extract_tags(text, topK=top_n_noun, withWeight=False, allowPOS=('ns', 'n', 'nt', 'nr', 'nrt', 'nz'))
    kw_v = jieba.analyse.extract_tags(text, topK=top_n_verb, withWeight=False, allowPOS=('v', 'vg', 'vd'))
    kw_a = jieba.analyse.extract_tags(text, topK=top_n_adj, withWeight=False, allowPOS=('ag', 'a', 'ad'))    
    
    df_n = pd.DataFrame({'token': kw_n, 'pos': '名词', 'source': source, 'comp': comp})
    df_v = pd.DataFrame({'token': kw_v, 'pos': '动词', 'source': source, 'comp': comp})
    df_a = pd.DataFrame({'token': kw_a, 'pos': '形容词', 'source': source, 'comp': comp})

    df_final = pd.concat([df_n, df_v, df_a])

    return df_final

#%%
kw_temp_q = extract_keywords(txt_temp_q, 50, 30, 30, '模板', '问句')
kw_temp_a = extract_keywords(txt_temp_q, 70, 30, 30, '模板', '答句')
kw_user_q = extract_keywords(txt_user_q, 50, 30, 30, '实际测试', '问句')
kw_user_a = extract_keywords(txt_user_a, 70, 30, 30, '实际测试', '答句')

kw_final = pd.concat([kw_temp_q, kw_temp_a, kw_user_q, kw_user_a])

#%%
# save the dataframe to disk
kw_final.to_csv(os.path.join(dir_path, "corpus_extraction_" + str(datetime.today().strftime('%Y%m%d')) + ".csv"))

#%%

# the following section is created to generate the list of frequent tokens. We use this to identify terms that should
# be added to the dictionary

# stopwords_file = open(os.path.join(dir_path, "hot/stopwords-master/百度停用词表.txt"), 'r', encoding = 'utf-8')
# stopwords_lst = [txt.rstrip() for txt in stopwords_file]
# stopwords_str = '|'.join(stopwords_lst)

#%%

text_lst = list(seg_lst_temp_q)

text_lst_clean = [re.sub(r'[？|？|?| |。|.|、|，|！|/|:|：|nan|Q|A|;|；|”|“]+', '', x) for x in text_lst]
text_lst_clean = [s for s in text_lst_clean if s]

#%%
# text_lst_clean = [re.sub(r'[' + stopwords_str + ']+', '', x) for x in text_lst_clean]
# text_lst_clean = [s for s in text_lst_clean if s]

#%%
df = pd.DataFrame({"token": text_lst_clean})

#%%
freq_summary = df.groupby(['token']).size().reset_index(name = 'counts').sort_values(['counts'], ascending=False)

freq_summary.size
#%%
freq_summary.to_csv(os.path.join(dir_path, "HoT_corpus_test.txt"), header=None, index=None, sep=' ')

