#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 10:24:01 2019

@author: huang
"""

import os
import time
from multiprocessing import Pool
## multi process util object 

class Mp():
    """
    abstract base class for Generator that yields info from each doc in a dir
    :param input: File or Dir
    """
    def __init__(self, input, mp_func):
        self.input = input
        self.mp_func = mp_func

    def chunks(self,l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]
            
    def multi_process_files(self,workers=os.cpu_count()-1,chunk_size=1000):
        #print('Start multiprocessing {} files in {} cores'.format(len(self.input),workers))
        #start = time.time()
        batch_size = workers*chunk_size*5
        batches = list(self.chunks(self.input, batch_size))
        p = Pool(workers)
        
        res = list()
        for i in range(len(batches)):
            #print('Processing {} - {} files ...'.format(i*batch_size,(i+1)*batch_size))
            rs = p.map(self.mp_func, batches[i],chunk_size)
            res.extend(rs)
        p.close()
        p.join()
        #end = time.time()            
        #print(time.strftime('%H:%M:%S', time.gmtime(end - start)))

        return res
    
    
#%%
if __name__ == "__main__":
#from mp_utils import Mp
    test = [1]*10000000
    def process(x):
        return (x+1)**2
    
    mp = Mp(test,process)
    #%%
    res = mp.multi_process_files()