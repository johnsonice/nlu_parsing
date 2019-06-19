#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 16:17:25 2019

@author: huang
"""

## convert raw input to knowledge input 

import pandas as pd

#%%
data_path = '../../data/raw/victor_pattern.xlsx'
out_data_path = '../../data/raw/victor_knowledge_input.xlsx'
df = pd.read_excel(data_path,sheet_name=None)
#%%

df_keys = list(df.keys())
df_keys = [k for k in df_keys if k != 'sets']
df_master = None
headers = ['intent','pattern']
        
#%%
df_master=pd.concat([df[k][headers] for k in df_keys],ignore_index=True)
df_master.columns = ['intent_id','pattern']
df_master= df_master.reindex(columns = [*df_master.columns.tolist(),'intent_class_1','intent_class_2'])
#%%
df_set = df['sets']
df_placeholder = pd.DataFrame(columns=['place_holder','value'])

#%%
## export to excel 
writer = pd.ExcelWriter(out_data_path, engine='xlsxwriter')
df_master.to_excel(writer, sheet_name='ask_pattern',index=False)
df_set.to_excel(writer, sheet_name='sets',index=False)
df_placeholder.to_excel(writer,sheet_name='place_holder',index=False)
writer.save()

#%%

#test_data_path = '../../data/raw/knowledge_input.xlsx'
#dd = pd.read_excel(test_data_path,sheet_name='sets')